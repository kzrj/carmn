import django_filters
from django.db.models import Q

from listings.models import (
    Availability,
    ConditionType,
    DamageStatus,
    Listing,
    ListingSource,
    ListingStatus,
    OwnersCount,
    PtsStatus,
    Steering,
)
from listings.services import annotate_has_photos, search_listings
from references.body_types import parse_body_type_filter_values
from references.models import BodyType, DriveType, FuelType, TransmissionType
from users.models import SellerType


class ListingFilter(django_filters.FilterSet):
    # Vehicle tree
    brand = django_filters.NumberFilter(field_name="brand_id")
    model = django_filters.NumberFilter(field_name="model_id")
    generation = django_filters.NumberFilter(field_name="generation_id")
    trim = django_filters.NumberFilter(field_name="trim_id")

    # Geo
    city = django_filters.NumberFilter(field_name="city_id")
    region = django_filters.NumberFilter(field_name="city__region_id")
    radius_km = django_filters.NumberFilter(method="filter_radius")

    # Tabs: all / used / new
    condition = django_filters.ChoiceFilter(field_name="condition_type", choices=ConditionType.choices)

    # Ranges
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")
    mileage_min = django_filters.NumberFilter(field_name="mileage", lookup_expr="gte")
    mileage_max = django_filters.NumberFilter(field_name="mileage", lookup_expr="lte")
    engine_volume_min = django_filters.NumberFilter(field_name="engine_volume", lookup_expr="gte")
    engine_volume_max = django_filters.NumberFilter(field_name="engine_volume", lookup_expr="lte")
    power_min = django_filters.NumberFilter(field_name="power_hp", lookup_expr="gte")
    power_max = django_filters.NumberFilter(field_name="power_hp", lookup_expr="lte")

    # References
    body_type = django_filters.CharFilter(method="filter_body_type")
    color = django_filters.NumberFilter(field_name="color_id")
    fuel = django_filters.NumberFilter(method="filter_fuel")
    transmission = django_filters.NumberFilter(method="filter_transmission")
    drive = django_filters.NumberFilter(method="filter_drive")
    import_country = django_filters.NumberFilter(field_name="import_country_id")
    brand_country = django_filters.NumberFilter(field_name="brand__country_id")

    # Enums
    source = django_filters.ChoiceFilter(choices=ListingSource.choices)
    status = django_filters.ChoiceFilter(choices=ListingStatus.choices)
    steering = django_filters.ChoiceFilter(choices=Steering.choices)
    pts_status = django_filters.ChoiceFilter(method="filter_pts_status")
    damage_status = django_filters.ChoiceFilter(method="filter_damage_status")
    seller_type = django_filters.ChoiceFilter(choices=SellerType.choices)
    availability = django_filters.ChoiceFilter(choices=Availability.choices)
    owners_count = django_filters.ChoiceFilter(method="filter_owners_count")

    # Booleans
    exchange_possible = django_filters.BooleanFilter()
    is_certified = django_filters.BooleanFilter()
    without_local_mileage = django_filters.BooleanFilter()
    customs_cleared = django_filters.BooleanFilter()
    has_photos = django_filters.BooleanFilter(method="filter_has_photos")
    unsold = django_filters.BooleanFilter(method="filter_unsold")

    # Text
    q = django_filters.CharFilter(method="filter_q")

    ordering = django_filters.OrderingFilter(
        fields=(
            ("published_at", "published_at"),
            ("price", "price"),
            ("year", "year"),
            ("mileage", "mileage"),
            ("view_count", "view_count"),
        ),
    )

    class Meta:
        model = Listing
        fields: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius_km: int | None = None

    def filter_radius(self, queryset, name, value):
        self._radius_km = int(value) if value else None
        return queryset

    def _parse_ref_id(self, value) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _filter_by_ref_id(self, queryset, ref_model, listing_field: str, trim_field: str, value):
        ref_id = self._parse_ref_id(value)
        if ref_id is None:
            return queryset
        if not ref_model.objects.filter(pk=ref_id).exists():
            return queryset.none()
        return queryset.filter(
            Q(**{listing_field: ref_id}) | Q(**{trim_field: ref_id})
        )

    def filter_fuel(self, queryset, name, value):
        return self._filter_by_ref_id(queryset, FuelType, "fuel_id", "trim__fuel_id", value)

    def filter_transmission(self, queryset, name, value):
        return self._filter_by_ref_id(
            queryset, TransmissionType, "transmission_id", "trim__transmission_id", value
        )

    def filter_drive(self, queryset, name, value):
        return self._filter_by_ref_id(queryset, DriveType, "drive_id", "trim__drive_id", value)

    def filter_body_type(self, queryset, name, value):
        raw = self.data.getlist("body_type") if hasattr(self.data, "getlist") else value
        if isinstance(raw, list) and len(raw) == 1 and "," in raw[0]:
            raw = raw[0]
        ids = parse_body_type_filter_values(raw if raw else value)
        if not ids:
            return queryset

        valid_ids = list(BodyType.objects.filter(pk__in=ids).values_list("pk", flat=True))
        if not valid_ids:
            return queryset.none()
        return queryset.filter(
            Q(body_type_id__in=valid_ids)
            | Q(trim__body_type_id__in=valid_ids)
            | Q(generation__body_type_id__in=valid_ids)
        )

    def filter_has_photos(self, queryset, name, value):
        qs = annotate_has_photos(queryset)
        if value:
            return qs.filter(_has_photos=True)
        return qs.filter(_has_photos=False)

    def filter_unsold(self, queryset, name, value):
        if value:
            return queryset.filter(status=ListingStatus.ACTIVE)
        return queryset.exclude(status=ListingStatus.ACTIVE)

    def filter_pts_status(self, queryset, name, value):
        if not value or value == PtsStatus.ANY:
            return queryset
        return queryset.filter(pts_status=value)

    def filter_damage_status(self, queryset, name, value):
        if not value or value == DamageStatus.ANY:
            return queryset
        return queryset.filter(damage_status=value)

    def filter_owners_count(self, queryset, name, value):
        if not value or value == OwnersCount.ANY:
            return queryset
        return queryset.filter(owners_count=value)

    def filter_q(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(description__icontains=value)
            | Q(brand__name_mn__icontains=value)
            | Q(brand__name_ru__icontains=value)
            | Q(brand__name_en__icontains=value)
            | Q(model__name_mn__icontains=value)
            | Q(model__name_ru__icontains=value)
            | Q(model__name_en__icontains=value)
            | Q(vin__icontains=value)
            | Q(chassis_number__icontains=value)
        )

    @property
    def qs(self):
        parent_qs = super().qs
        city_id = self.data.get("city")
        radius_km = self._radius_km or self.data.get("radius_km")
        if city_id and radius_km:
            try:
                return search_listings(
                    parent_qs,
                    city_id=int(city_id),
                    radius_km=int(radius_km),
                )
            except (TypeError, ValueError):
                pass
        return parent_qs
