from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import ExchangeRate

from geo.models import City, Region
from listings.models import ConditionType, Listing, Steering
from references.body_types import ensure_canonical_body_types
from references.models import BodyType, Color, Country, DriveType, FuelType, TransmissionType
from references.vehicle_refs import ensure_canonical_vehicle_refs
from users.models import SellerProfile, SellerType, User
from vehicles.models import Brand, Generation, Model, Trim


def upsert_ref(model, slug: str, **fields):
    obj, created = model.objects.update_or_create(slug=slug, defaults=fields)
    return obj, created


class Command(BaseCommand):
    help = "Seed minimal catalog data for local development"

    def handle(self, *args, **options):
        stats = {"created": 0, "updated": 0}

        def track(obj, created: bool):
            stats["created" if created else "updated"] += 1
            return obj

        rate, c = ExchangeRate.objects.update_or_create(
            currency="USD",
            date=timezone.localdate(),
            defaults={"rate_to_mnt": Decimal("3450.00")},
        )
        track(rate, c)

        japan, c = upsert_ref(
            Country,
            "japan",
            name_mn="Япон",
            name_ru="Япония",
            name_en="Japan",
            iso_code="JP",
        )
        track(japan, c)

        korea, c = upsert_ref(
            Country,
            "korea",
            name_mn="Солонгос",
            name_ru="Корея",
            name_en="Korea",
            iso_code="KR",
        )
        track(korea, c)

        ub_region, c = upsert_ref(
            Region,
            "ulaanbaatar",
            name_mn="Улаанбаатар",
            name_ru="Улан-Батор",
            name_en="Ulaanbaatar",
        )
        track(ub_region, c)

        darkhan_region, c = upsert_ref(
            Region,
            "darkhan-uul",
            name_mn="Дархан-Уул",
            name_ru="Дархан-Уул",
            name_en="Darkhan-Uul",
        )
        track(darkhan_region, c)

        ub_city, c = upsert_ref(
            City,
            "ulaanbaatar",
            region=ub_region,
            name_mn="Улаанбаатар",
            name_ru="Улан-Батор",
            name_en="Ulaanbaatar",
            latitude=Decimal("47.886400"),
            longitude=Decimal("106.905700"),
        )
        track(ub_city, c)

        darkhan_city, c = upsert_ref(
            City,
            "darkhan",
            region=darkhan_region,
            name_mn="Дархан",
            name_ru="Дархан",
            name_en="Darkhan",
            latitude=Decimal("49.486900"),
            longitude=Decimal("105.942600"),
        )
        track(darkhan_city, c)

        ensure_canonical_body_types()
        ensure_canonical_vehicle_refs()
        sedan = BodyType.objects.get(slug="sedan")
        suv = BodyType.objects.get(slug="suv-5d")
        track(sedan, False)
        track(suv, False)

        white, c = upsert_ref(Color, "white", name_mn="Цагаан", name_ru="Белый", name_en="White")
        track(white, c)
        black, c = upsert_ref(Color, "black", name_mn="Хар", name_ru="Чёрный", name_en="Black")
        track(black, c)
        silver, c = upsert_ref(
            Color, "silver", name_mn="Мөнгөлөг", name_ru="Серебристый", name_en="Silver"
        )
        track(silver, c)

        petrol = FuelType.objects.get(slug="petrol")
        hybrid = FuelType.objects.get(slug="hybrid")
        track(petrol, False)
        track(hybrid, False)

        auto = TransmissionType.objects.get(slug="akpp")
        fwd = DriveType.objects.get(slug="fwd")
        awd = DriveType.objects.get(slug="awd")
        track(auto, False)
        track(fwd, False)
        track(awd, False)

        toyota, c = upsert_ref(
            Brand,
            "toyota",
            country=japan,
            name_mn="Toyota",
            name_ru="Toyota",
            name_en="Toyota",
        )
        track(toyota, c)
        honda, c = upsert_ref(
            Brand,
            "honda",
            country=japan,
            name_mn="Honda",
            name_ru="Honda",
            name_en="Honda",
        )
        track(honda, c)

        camry, c = upsert_ref(
            Model,
            "toyota-camry",
            brand=toyota,
            name_mn="Camry",
            name_ru="Camry",
            name_en="Camry",
        )
        track(camry, c)
        prius, c = upsert_ref(
            Model,
            "toyota-prius",
            brand=toyota,
            name_mn="Prius",
            name_ru="Prius",
            name_en="Prius",
        )
        track(prius, c)
        fit, c = upsert_ref(
            Model,
            "honda-fit",
            brand=honda,
            name_mn="Fit",
            name_ru="Fit",
            name_en="Fit",
        )
        track(fit, c)

        camry_gen, c = upsert_ref(
            Generation,
            "toyota-camry-xv70",
            model=camry,
            name_mn="XV70",
            name_ru="XV70",
            name_en="XV70",
            year_from=2017,
            year_to=2024,
        )
        track(camry_gen, c)
        prius_gen, c = upsert_ref(
            Generation,
            "toyota-prius-xw50",
            model=prius,
            name_mn="XW50",
            name_ru="XW50",
            name_en="XW50",
            year_from=2015,
            year_to=2022,
        )
        track(prius_gen, c)

        camry_trim, c = upsert_ref(
            Trim,
            "toyota-camry-25-elegance",
            generation=camry_gen,
            name_mn="2.5 AT Elegance",
            name_ru="2.5 AT Elegance",
            name_en="2.5 AT Elegance",
        )
        track(camry_trim, c)
        prius_trim, c = upsert_ref(
            Trim,
            "toyota-prius-s",
            generation=prius_gen,
            name_mn="S Hybrid",
            name_ru="S Hybrid",
            name_en="S Hybrid",
        )
        track(prius_trim, c)

        user, created = User.objects.get_or_create(
            phone="99119911",
            defaults={"is_active": True},
        )
        if created:
            user.set_password("demo1234")
            user.save()
            stats["created"] += 1
        else:
            stats["updated"] += 1

        SellerProfile.objects.update_or_create(
            user=user,
            defaults={
                "seller_type": SellerType.PRIVATE,
                "display_name": "Бат",
            },
        )

        listings_data = [
            {
                "brand": toyota,
                "model": camry,
                "generation": camry_gen,
                "trim": camry_trim,
                "city": ub_city,
                "year": 2019,
                "price": 58_000_000,
                "mileage": 74_000,
                "condition_type": ConditionType.USED,
                "body_type": sedan,
                "color": white,
                "fuel": petrol,
                "transmission": auto,
                "drive": fwd,
                "engine_volume": Decimal("2.5"),
                "power_hp": 181,
                "steering": Steering.LEFT,
                "description": "UB дотор сайн байдалтай Camry. Японоос орж ирсэн.",
                "without_local_mileage": False,
                "import_country": japan,
            },
            {
                "brand": toyota,
                "model": prius,
                "generation": prius_gen,
                "trim": prius_trim,
                "city": ub_city,
                "year": 2018,
                "price": 42_000_000,
                "mileage": 112_000,
                "condition_type": ConditionType.USED,
                "body_type": sedan,
                "color": silver,
                "fuel": hybrid,
                "transmission": auto,
                "drive": fwd,
                "engine_volume": Decimal("1.8"),
                "power_hp": 122,
                "steering": Steering.RIGHT,
                "description": "Бензин хэмнэлттэй Prius. Баруун руль.",
                "without_local_mileage": True,
                "import_country": japan,
            },
            {
                "brand": honda,
                "model": fit,
                "generation": None,
                "trim": None,
                "city": darkhan_city,
                "year": 2016,
                "price": 28_000_000,
                "mileage": 98_500,
                "condition_type": ConditionType.USED,
                "body_type": sedan,
                "color": black,
                "fuel": petrol,
                "transmission": auto,
                "drive": fwd,
                "engine_volume": Decimal("1.5"),
                "power_hp": 131,
                "steering": Steering.RIGHT,
                "description": "Дарханд байршилтай Honda Fit.",
                "without_local_mileage": False,
                "import_country": japan,
            },
        ]

        for data in listings_data:
            _, listing_created = Listing.objects.update_or_create(
                user=user,
                brand=data["brand"],
                model=data["model"],
                year=data["year"],
                city=data["city"],
                defaults={
                    **data,
                    "seller_type": SellerType.PRIVATE,
                },
            )
            track(_, listing_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed done: {stats['created']} created, {stats['updated']} updated. "
                f"Login: phone 99119911 / demo1234"
            )
        )
