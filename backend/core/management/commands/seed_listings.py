from __future__ import annotations

import random
from decimal import Decimal
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.generation_photos import GenerationPhotoCatalog, default_parsed_dir
from geo.models import City, Region
from listings.models import (
    Availability,
    ConditionType,
    Listing,
    ListingPhoto,
    ListingSource,
    ListingStatus,
    Steering,
)
from references.models import Color, Country
from users.models import SellerProfile, SellerType, User
from vehicles.models import Trim

def upsert_ref(model, slug: str, **fields):
    return model.objects.update_or_create(slug=slug, defaults=fields)[0]


DESCRIPTIONS = [
    "Сайн байдалтай, гоё засварлагдсан.",
    "Японоос шинээр орж ирсэн, бүртгэлгүй.",
    "Гэр бүлийн хэрэглээнд, осолгүй.",
    "Бүх зураг бодит, үзэж авч болно.",
    "Шалгалт, засвар шаардлагагүй.",
    "Бензин хэмнэлттэй, эдийн засгийн.",
    "Зардал багатай, найдвартай загвар.",
    "Дотор цэвэр, гадна гоё.",
    "Барьян руль, Монголд бага явсан.",
    "Шинэ шинэчилсэн дугуй, аккумулятор.",
    "UB дотор үзэж болно, үнэ тохирно.",
    "Шууд авч явах боломжтой.",
    "Компьютерийн шалгалт хийсэн.",
    "Солонгосоос орж ирсэн, гоё комплектаци.",
    "Хүүхдийн суудал, камера, круиз.",
]


class Command(BaseCommand):
    help = "Seed diverse test listings from imported vehicle catalog"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--count", type=int, default=100, help="Number of listings to create")
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete previous seed listings (external_id seed-*) before creating new ones",
        )
        parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible data")
        parser.add_argument(
            "--no-photos",
            action="store_true",
            help="Skip downloading generation photos from drom.ru",
        )
        parser.add_argument(
            "--parsed-dir",
            default=None,
            help="Parsed JSON directory (default: scripts/drom/parsed or /data/drom/parsed)",
        )
        parser.add_argument(
            "--photo-delay",
            type=float,
            default=0.3,
            help="Delay between photo downloads in seconds",
        )

    def handle(self, *args, **options) -> None:
        count = options["count"]
        if count < 1:
            raise CommandError("--count must be at least 1")

        random.seed(options["seed"])

        trims = list(
            Trim.objects.select_related(
                "generation",
                "generation__model",
                "generation__model__brand",
                "generation__body_type",
                "body_type",
                "fuel",
                "transmission",
                "drive",
            ).order_by("id")
        )
        if not trims:
            raise CommandError("Catalog is empty. Run: python manage.py import_drom --replace")

        cities = self._ensure_geo()
        colors = self._ensure_colors()
        countries = self._ensure_countries()
        sellers = self._ensure_sellers()

        if options["clear"]:
            deleted, _ = Listing.objects.filter(external_id__startswith="seed-").delete()
            self.stdout.write(f"Cleared {deleted} previous seed listings")

        parsed_dir = Path(options["parsed_dir"]) if options["parsed_dir"] else default_parsed_dir()
        photo_catalog = None
        if not options["no_photos"]:
            if not parsed_dir.is_dir():
                self.stdout.write(
                    self.style.WARNING(f"Parsed dir not found ({parsed_dir}), seeding without photos")
                )
            else:
                photo_catalog = GenerationPhotoCatalog(parsed_dir, delay_sec=options["photo_delay"])

        trim_pool = trims.copy()
        random.shuffle(trim_pool)

        created = 0
        photos_attached = 0
        photos_missing = 0
        with transaction.atomic():
            for index in range(count):
                profile = random.choice(sellers)
                listing = self._build_listing(
                    index=index,
                    trim=trim_pool[index % len(trim_pool)],
                    cities=cities,
                    colors=colors,
                    countries=countries,
                    user=profile["user"],
                    seller_type=profile["seller_type"],
                )
                listing.save()
                created += 1

                if not options["no_photos"] and listing.generation_id:
                    generation = listing.generation
                    attached = self._attach_listing_photo(
                        listing=listing,
                        generation=generation,
                        photo_catalog=photo_catalog,
                    )
                    if attached:
                        photos_attached += 1
                    else:
                        photos_missing += 1

        message = (
            f"Created {created} test listings. "
            f"Sellers: {', '.join(p['phone'] for p in sellers)} / password: demo1234"
        )
        if photo_catalog:
            message += f". Photos: {photos_attached} attached, {photos_missing} missing"
        self.stdout.write(self.style.SUCCESS(message))

    def _attach_listing_photo(self, *, listing, generation, photo_catalog) -> bool:
        if generation.photo:
            generation.photo.open("rb")
            try:
                filename = generation.photo.name.rsplit("/", 1)[-1]
                content = ContentFile(generation.photo.read(), name=filename)
            finally:
                generation.photo.close()
            ListingPhoto.objects.create(
                listing=listing,
                image=content,
                sort_order=0,
                is_primary=True,
            )
            return True

        if not photo_catalog:
            return False

        model = generation.model
        brand = model.brand
        photo_url = photo_catalog.lookup(
            brand_slug=brand.slug,
            model_slug=model.slug,
            generation_slug_value=generation.slug,
        )
        if not photo_url:
            return False

        image = photo_catalog.fetch_image(photo_url)
        if not image:
            return False

        ListingPhoto.objects.create(
            listing=listing,
            image=image,
            sort_order=0,
            is_primary=True,
        )
        return True

    def _ensure_geo(self) -> list[City]:
        ub_region = upsert_ref(
            Region,
            "ulaanbaatar",
            name_mn="Улаанбаатар",
            name_ru="Улан-Батор",
            name_en="Ulaanbaatar",
        )
        darkhan_region = upsert_ref(
            Region,
            "darkhan-uul",
            name_mn="Дархан-Уул",
            name_ru="Дархан-Уул",
            name_en="Darkhan-Uul",
        )
        erdenet_region = upsert_ref(
            Region,
            "orkhon",
            name_mn="Орхон",
            name_ru="Орхон",
            name_en="Orkhon",
        )

        return [
            upsert_ref(
                City,
                "ulaanbaatar",
                region=ub_region,
                name_mn="Улаанбаатар",
                name_ru="Улан-Батор",
                name_en="Ulaanbaatar",
                latitude=Decimal("47.886400"),
                longitude=Decimal("106.905700"),
            ),
            upsert_ref(
                City,
                "darkhan",
                region=darkhan_region,
                name_mn="Дархан",
                name_ru="Дархан",
                name_en="Darkhan",
                latitude=Decimal("49.486900"),
                longitude=Decimal("105.942600"),
            ),
            upsert_ref(
                City,
                "erdenet",
                region=erdenet_region,
                name_mn="Эрдэнэт",
                name_ru="Эрдэнэт",
                name_en="Erdenet",
                latitude=Decimal("49.027800"),
                longitude=Decimal("104.045600"),
            ),
        ]

    def _ensure_colors(self) -> list[Color]:
        specs = [
            ("white", "Цагаан", "Белый", "White"),
            ("black", "Хар", "Чёрный", "Black"),
            ("silver", "Мөнгөлөг", "Серебристый", "Silver"),
            ("grey", "Саарал", "Серый", "Grey"),
            ("blue", "Хөх", "Синий", "Blue"),
            ("red", "Улаан", "Красный", "Red"),
            ("green", "Ногоон", "Зелёный", "Green"),
            ("brown", "Бор", "Коричневый", "Brown"),
        ]
        return [
            upsert_ref(Color, slug, name_mn=mn, name_ru=ru, name_en=en)
            for slug, mn, ru, en in specs
        ]

    def _ensure_countries(self) -> list[Country]:
        specs = [
            ("japan", "Япон", "Япония", "Japan", "JP"),
            ("korea", "Солонгос", "Корея", "Korea", "KR"),
            ("germany", "Герман", "Германия", "Germany", "DE"),
            ("usa", "Америк", "США", "USA", "US"),
            ("russia", "Орос", "Россия", "Russia", "RU"),
        ]
        return [
            upsert_ref(
                Country,
                slug,
                name_mn=mn,
                name_ru=ru,
                name_en=en,
                iso_code=iso,
            )
            for slug, mn, ru, en, iso in specs
        ]

    def _ensure_sellers(self) -> list[dict]:
        profiles = [
            ("99110001", SellerType.PRIVATE, "Бат"),
            ("99110002", SellerType.PRIVATE, "Сараа"),
            ("99110003", SellerType.OWNER, "Тэмүүжин"),
            ("99110004", SellerType.COMPANY, "AutoTrade UB"),
            ("99110005", SellerType.PRIVATE, "Оyu"),
            ("99110006", SellerType.COMPANY, "Drive MN"),
        ]
        sellers = []
        for phone, seller_type, display_name in profiles:
            user, created = User.objects.get_or_create(phone=phone, defaults={"is_active": True})
            if created:
                user.set_password("demo1234")
                user.save()
            SellerProfile.objects.update_or_create(
                user=user,
                defaults={
                    "seller_type": seller_type,
                    "display_name": display_name,
                    "company_name": display_name if seller_type == SellerType.COMPANY else "",
                },
            )
            sellers.append({"user": user, "phone": phone, "seller_type": seller_type})
        return sellers

    def _build_listing(
        self,
        *,
        index: int,
        trim: Trim,
        cities: list[City],
        colors: list[Color],
        countries: list[Country],
        user: User,
        seller_type: str,
    ) -> Listing:
        generation = trim.generation
        model = generation.model
        brand = model.brand

        use_generation = random.random() < 0.85
        use_trim = use_generation and random.random() < 0.8

        year_from = generation.year_from or 2005
        year_to = generation.year_to or 2025
        if year_from > year_to:
            year_from, year_to = year_to, year_from
        year = random.randint(year_from, year_to)

        base_price = 18_000_000 + (2026 - year) * 1_200_000
        price = base_price + random.randint(-5_000_000, 12_000_000)
        price = max(8_000_000, price)

        mileage = None
        condition = ConditionType.USED
        if random.random() < 0.08:
            condition = ConditionType.NEW
            mileage = random.randint(0, 50)
        else:
            age = max(1, 2026 - year)
            mileage = random.randint(15_000, min(280_000, age * 22_000 + random.randint(0, 40_000)))

        body_type = trim.body_type or generation.body_type
        fuel = trim.fuel
        transmission = trim.transmission
        drive = trim.drive

        engine_volume = Decimal(str(round(random.choice([1.3, 1.5, 1.6, 1.8, 2.0, 2.4, 2.5, 3.0, 3.5]), 1)))
        power_hp = random.randint(90, 280)

        steering = Steering.RIGHT if random.random() < 0.65 else Steering.LEFT
        without_local = steering == Steering.RIGHT and random.random() < 0.7

        brand_name = brand.name_ru or brand.name_en or brand.slug
        model_name = model.name_ru or model.name_en or model.slug
        trim_name = trim.name_ru if use_trim else ""
        title_bits = [brand_name, model_name, str(year)]
        if trim_name:
            title_bits.append(trim_name)

        return Listing(
            user=user,
            brand=brand,
            model=model,
            generation=generation if use_generation else None,
            trim=trim if use_trim else None,
            city=random.choice(cities),
            year=year,
            price=price,
            mileage=mileage,
            condition_type=condition,
            status=ListingStatus.ACTIVE,
            source=ListingSource.USER,
            external_id=f"seed-{index + 1:04d}",
            body_type=body_type,
            color=random.choice(colors),
            fuel=fuel,
            transmission=transmission,
            drive=drive,
            engine_volume=engine_volume,
            power_hp=power_hp,
            steering=steering,
            seller_type=seller_type,
            availability=random.choice(
                [Availability.IN_STOCK, Availability.IN_STOCK, Availability.IN_TRANSIT, Availability.ON_ORDER]
            ),
            exchange_possible=random.random() < 0.25,
            is_certified=random.random() < 0.1,
            without_local_mileage=without_local,
            customs_cleared=random.random() < 0.92,
            import_country=random.choice(countries),
            description=f"{' '.join(title_bits)}. {random.choice(DESCRIPTIONS)}",
            view_count=random.randint(0, 450),
        )
