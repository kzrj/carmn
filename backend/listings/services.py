import hashlib
import math
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Exists, F, OuterRef, Q, QuerySet, Value
from django.utils import timezone

from core.services import resolve_listing_price
from geo.models import City
from listings.models import (
    Listing,
    ListingPhoto,
    ListingPriceHistory,
    ListingSource,
    ListingStatus,
    ListingView,
    Steering,
    UserFavorite,
)
from users.models import User
from vehicles.models import Brand, Generation, Model, Trim

VIEW_DEBOUNCE_MINUTES = 30


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def filter_by_radius(qs: QuerySet[Listing], city: City, radius_km: int) -> QuerySet[Listing]:
    if radius_km <= 0:
        return qs.filter(city=city)

    center_lat = float(city.latitude)
    center_lng = float(city.longitude)
    city_ids = [
        c.id
        for c in City.objects.only("id", "latitude", "longitude")
        if _haversine_km(center_lat, center_lng, float(c.latitude), float(c.longitude)) <= radius_km
    ]
    return qs.filter(city_id__in=city_ids)


def annotate_has_photos(qs: QuerySet[Listing]) -> QuerySet[Listing]:
    photos = ListingPhoto.objects.filter(listing_id=OuterRef("pk"))
    return qs.annotate(_has_photos=Exists(photos))


def annotate_is_favorited(qs: QuerySet[Listing], user: User | None) -> QuerySet[Listing]:
    if not user or not user.is_authenticated:
        return qs.annotate(_is_favorited=Value(False))
    favorites = UserFavorite.objects.filter(listing_id=OuterRef("pk"), user_id=user.id)
    return qs.annotate(_is_favorited=Exists(favorites))


def search_listings(
    qs: QuerySet[Listing] | None = None,
    *,
    q: str | None = None,
    city_id: int | None = None,
    radius_km: int | None = None,
    region_id: int | None = None,
    brand_country_id: int | None = None,
    user: User | None = None,
) -> QuerySet[Listing]:
    if qs is None:
        qs = Listing.objects.filter(status=ListingStatus.ACTIVE)
    qs = qs.select_related(
        "brand",
        "brand__country",
        "model",
        "generation",
        "trim",
        "city",
        "city__region",
        "body_type",
        "color",
        "fuel",
        "transmission",
        "drive",
        "import_country",
        "user",
        "user__seller_profile",
    ).prefetch_related("photos")
    qs = annotate_is_favorited(qs, user)

    if q:
        qs = qs.filter(
            Q(description__icontains=q)
            | Q(brand__name_mn__icontains=q)
            | Q(brand__name_ru__icontains=q)
            | Q(brand__name_en__icontains=q)
            | Q(model__name_mn__icontains=q)
            | Q(model__name_ru__icontains=q)
            | Q(model__name_en__icontains=q)
            | Q(vin__icontains=q)
            | Q(chassis_number__icontains=q)
        )

    if region_id:
        qs = qs.filter(city__region_id=region_id)

    if city_id and radius_km:
        city = City.objects.filter(pk=city_id).first()
        if city:
            qs = filter_by_radius(qs, city, int(radius_km))
    elif city_id:
        qs = qs.filter(city_id=city_id)

    if brand_country_id:
        qs = qs.filter(brand__country_id=brand_country_id)

    return qs


def validate_vehicle_tree(
    *,
    brand: Brand,
    model: Model,
    generation: Generation | None,
    trim: Trim | None,
) -> None:
    if model.brand_id != brand.id:
        raise ValidationError("Model does not belong to the selected brand.")
    if generation and generation.model_id != model.id:
        raise ValidationError("Generation does not belong to the selected model.")
    if trim:
        if not generation:
            raise ValidationError("Generation is required when trim is specified.")
        if trim.generation_id != generation.id:
            raise ValidationError("Trim does not belong to the selected generation.")


def normalize_vin(vin: str) -> str:
    return vin.strip().upper()


def record_price_change(
    *,
    listing: Listing,
    old_price: int,
    new_price: int,
    changed_by: User | None = None,
) -> None:
    if old_price == new_price:
        return
    ListingPriceHistory.objects.create(
        listing=listing,
        old_price=old_price,
        new_price=new_price,
        changed_by=changed_by,
    )


def _client_ip_hash(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")
    return hashlib.sha256(ip.encode()).hexdigest()


def record_listing_view(*, listing: Listing, request, user: User | None = None) -> bool:
    if listing.status != ListingStatus.ACTIVE:
        return False

    ip_hash = _client_ip_hash(request)
    since = timezone.now() - timedelta(minutes=VIEW_DEBOUNCE_MINUTES)
    already_viewed = ListingView.objects.filter(
        listing=listing,
        ip_hash=ip_hash,
        viewed_at__gte=since,
    ).exists()
    if already_viewed:
        return False

    ListingView.objects.create(listing=listing, user=user if user and user.is_authenticated else None, ip_hash=ip_hash)
    Listing.objects.filter(pk=listing.pk).update(view_count=F("view_count") + 1)
    listing.view_count += 1
    return True


def add_favorite(*, user: User, listing: Listing) -> UserFavorite:
    favorite, _ = UserFavorite.objects.get_or_create(user=user, listing=listing)
    return favorite


def remove_favorite(*, user: User, listing: Listing) -> bool:
    deleted, _ = UserFavorite.objects.filter(user=user, listing=listing).delete()
    return deleted > 0


def _listing_kwargs(data: dict, *, listing: Listing | None = None) -> dict:
    price, price_usd = resolve_listing_price(
        price=data.get("price"),
        price_usd=data.get("price_usd"),
        fallback_price=listing.price if listing else None,
        fallback_price_usd=listing.price_usd if listing else None,
    )
    vin = normalize_vin(data.get("vin", ""))

    return {
        "brand": data["brand"],
        "model": data["model"],
        "generation": data.get("generation"),
        "trim": data.get("trim"),
        "city": data["city"],
        "year": data["year"],
        "price": price,
        "price_usd": price_usd,
        "mileage": data.get("mileage"),
        "condition_type": data["condition_type"],
        "body_type": data.get("body_type"),
        "color": data.get("color"),
        "fuel": data.get("fuel"),
        "transmission": data.get("transmission"),
        "drive": data.get("drive"),
        "engine_volume": data.get("engine_volume"),
        "power_hp": data.get("power_hp"),
        "steering": data.get("steering") or Steering.LEFT,
        "pts_status": data.get("pts_status") or Listing._meta.get_field("pts_status").default,
        "damage_status": data.get("damage_status") or Listing._meta.get_field("damage_status").default,
        "seller_type": data.get("seller_type"),
        "availability": data.get("availability") or Listing._meta.get_field("availability").default,
        "owners_count": data.get("owners_count"),
        "exchange_possible": data.get("exchange_possible", False),
        "is_certified": data.get("is_certified", False),
        "without_local_mileage": data.get("without_local_mileage", False),
        "customs_cleared": data.get("customs_cleared", True),
        "import_country": data.get("import_country"),
        "description": data.get("description", ""),
        "vin": vin,
        "chassis_number": (data.get("chassis_number") or "").strip(),
        "source": data.get("source") or ListingSource.USER,
        "external_id": (data.get("external_id") or "").strip(),
        "external_url": data.get("external_url") or "",
        "parsed_at": data.get("parsed_at"),
        "status": data.get("status") or ListingStatus.ACTIVE,
    }


@transaction.atomic
def create_listing(*, user: User, data: dict, photos: list | None = None) -> Listing:
    brand = data["brand"]
    model = data["model"]
    generation = data.get("generation")
    trim = data.get("trim")
    validate_vehicle_tree(brand=brand, model=model, generation=generation, trim=trim)

    seller_type = data.get("seller_type")
    if not seller_type and hasattr(user, "seller_profile"):
        seller_type = user.seller_profile.seller_type

    kwargs = _listing_kwargs(data)
    kwargs["user"] = user
    kwargs["seller_type"] = seller_type or user.seller_profile.seller_type

    listing = Listing.objects.create(**kwargs)

    if photos:
        for idx, photo in enumerate(photos):
            ListingPhoto.objects.create(
                listing=listing,
                image=photo,
                sort_order=idx,
                is_primary=idx == 0,
            )

    return listing


@transaction.atomic
def update_listing(*, listing: Listing, data: dict, changed_by: User | None = None) -> Listing:
    brand = data.get("brand", listing.brand)
    model = data.get("model", listing.model)
    generation = data.get("generation", listing.generation)
    trim = data.get("trim", listing.trim)
    validate_vehicle_tree(brand=brand, model=model, generation=generation, trim=trim)

    old_price = listing.price
    kwargs = _listing_kwargs({**{
        "brand": listing.brand,
        "model": listing.model,
        "generation": listing.generation,
        "trim": listing.trim,
        "city": listing.city,
        "year": listing.year,
        "price": listing.price,
        "price_usd": listing.price_usd,
        "mileage": listing.mileage,
        "condition_type": listing.condition_type,
        "body_type": listing.body_type,
        "color": listing.color,
        "fuel": listing.fuel,
        "transmission": listing.transmission,
        "drive": listing.drive,
        "engine_volume": listing.engine_volume,
        "power_hp": listing.power_hp,
        "steering": listing.steering,
        "pts_status": listing.pts_status,
        "damage_status": listing.damage_status,
        "seller_type": listing.seller_type,
        "availability": listing.availability,
        "owners_count": listing.owners_count,
        "exchange_possible": listing.exchange_possible,
        "is_certified": listing.is_certified,
        "without_local_mileage": listing.without_local_mileage,
        "customs_cleared": listing.customs_cleared,
        "import_country": listing.import_country,
        "description": listing.description,
        "vin": listing.vin,
        "chassis_number": listing.chassis_number,
        "source": listing.source,
        "external_id": listing.external_id,
        "external_url": listing.external_url,
        "parsed_at": listing.parsed_at,
        "status": listing.status,
    }, **data}, listing=listing)

    for field, value in kwargs.items():
        setattr(listing, field, value)

    listing.save()
    record_price_change(listing=listing, old_price=old_price, new_price=listing.price, changed_by=changed_by)
    return listing
