"""Smoke tests: canonical refs, filters by id, listing write validation."""

from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from geo.models import City, Region
from listings.filters import ListingFilter
from listings.models import Availability, ConditionType, Listing, ListingStatus
from listings.serializers import ListingWriteSerializer
from references.body_types import CANONICAL_BODY_TYPE_SLUGS, ensure_canonical_body_types
from references.models import BodyType, Color, DriveType, FuelType, TransmissionType
from references.vehicle_refs import (
    CANONICAL_DRIVE_SLUGS,
    CANONICAL_FUEL_SLUGS,
    CANONICAL_TRANSMISSION_SLUGS,
    ensure_canonical_vehicle_refs,
)
from users.models import SellerProfile, SellerType, User
from vehicles.models import Brand, Generation, Model, Trim


def _ensure_catalog_refs() -> None:
    ensure_canonical_body_types()
    ensure_canonical_vehicle_refs()


class CanonicalSmokeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        _ensure_catalog_refs()

        cls.petrol = FuelType.objects.get(slug="petrol")
        cls.diesel = FuelType.objects.get(slug="diesel")
        cls.sedan = BodyType.objects.get(slug="sedan")
        cls.suv = BodyType.objects.get(slug="suv-5d")
        cls.akpp = TransmissionType.objects.get(slug="akpp")
        cls.fwd = DriveType.objects.get(slug="fwd")

        region = Region.objects.create(
            slug="test-region",
            name_mn="Test",
            name_ru="Test",
            name_en="Test",
        )
        cls.city = City.objects.create(
            slug="test-city",
            region=region,
            name_mn="Test",
            name_ru="Test",
            name_en="Test",
            latitude=Decimal("47.886400"),
            longitude=Decimal("106.905700"),
        )
        cls.brand = Brand.objects.create(
            slug="test-brand",
            name_mn="Test",
            name_ru="Test",
            name_en="Test",
        )
        cls.model = Model.objects.create(
            slug="test-model",
            brand=cls.brand,
            name_mn="Test",
            name_ru="Test",
            name_en="Test",
        )
        cls.generation = Generation.objects.create(
            slug="test-gen",
            model=cls.model,
            name_mn="Gen",
            name_ru="Gen",
            name_en="Gen",
            year_from=2020,
            year_to=2024,
            body_type=cls.sedan,
        )
        cls.trim_diesel = Trim.objects.create(
            slug="test-trim-diesel",
            generation=cls.generation,
            name_mn="2.0 AT",
            name_ru="2.0 AT",
            name_en="2.0 AT",
            fuel=cls.diesel,
            transmission=cls.akpp,
            drive=cls.fwd,
            body_type=cls.sedan,
        )

        cls.user = User.objects.create_user(phone="99001122", password="test-pass")
        SellerProfile.objects.create(
            user=cls.user,
            seller_type=SellerType.PRIVATE,
            display_name="Test",
        )
        cls.color = Color.objects.create(
            slug="test-white",
            name_mn="White",
            name_ru="White",
            name_en="White",
        )

        cls.listing_direct = Listing.objects.create(
            user=cls.user,
            brand=cls.brand,
            model=cls.model,
            generation=cls.generation,
            city=cls.city,
            year=2021,
            price=50_000_000,
            condition_type=ConditionType.USED,
            status=ListingStatus.ACTIVE,
            seller_type=SellerType.PRIVATE,
            availability=Availability.IN_STOCK,
            fuel=cls.petrol,
            body_type=cls.sedan,
        )
        cls.listing_via_trim = Listing.objects.create(
            user=cls.user,
            brand=cls.brand,
            model=cls.model,
            generation=cls.generation,
            trim=cls.trim_diesel,
            city=cls.city,
            year=2022,
            price=55_000_000,
            condition_type=ConditionType.USED,
            status=ListingStatus.ACTIVE,
            seller_type=SellerType.PRIVATE,
            availability=Availability.IN_STOCK,
            fuel=None,
            body_type=None,
        )

    def _active_qs(self):
        return Listing.objects.filter(status=ListingStatus.ACTIVE)

    def test_reference_tables_only_canonical_slugs(self):
        self.assertFalse(
            BodyType.objects.exclude(slug__in=CANONICAL_BODY_TYPE_SLUGS).exists()
        )
        self.assertFalse(FuelType.objects.exclude(slug__in=CANONICAL_FUEL_SLUGS).exists())
        self.assertFalse(
            TransmissionType.objects.exclude(slug__in=CANONICAL_TRANSMISSION_SLUGS).exists()
        )
        self.assertFalse(DriveType.objects.exclude(slug__in=CANONICAL_DRIVE_SLUGS).exists())

    def test_filter_fuel_by_listing_fk(self):
        fs = ListingFilter({"fuel": str(self.petrol.pk)}, queryset=self._active_qs())
        self.assertTrue(fs.is_valid())
        ids = set(fs.qs.values_list("pk", flat=True))
        self.assertEqual(ids, {self.listing_direct.pk})

    def test_filter_fuel_by_trim_fk(self):
        fs = ListingFilter({"fuel": str(self.diesel.pk)}, queryset=self._active_qs())
        self.assertTrue(fs.is_valid())
        ids = set(fs.qs.values_list("pk", flat=True))
        self.assertEqual(ids, {self.listing_via_trim.pk})

    def test_filter_body_type(self):
        fs = ListingFilter({"body_type": str(self.sedan.pk)}, queryset=self._active_qs())
        self.assertTrue(fs.is_valid())
        ids = set(fs.qs.values_list("pk", flat=True))
        self.assertIn(self.listing_direct.pk, ids)
        self.assertIn(self.listing_via_trim.pk, ids)

    def test_filter_body_type_comma_separated(self):
        fs = ListingFilter(
            {"body_type": f"{self.sedan.pk},{self.suv.pk}"},
            queryset=self._active_qs(),
        )
        self.assertTrue(fs.is_valid())
        self.assertGreaterEqual(fs.qs.count(), 2)

    def test_filter_invalid_ref_returns_empty(self):
        fs = ListingFilter({"fuel": "999999"}, queryset=self._active_qs())
        self.assertTrue(fs.is_valid())
        self.assertEqual(fs.qs.count(), 0)

    def test_write_serializer_rejects_non_canonical_body_type(self):
        junk = BodyType.objects.create(
            slug="legacy-junk-body",
            name_mn="Junk",
            name_ru="Junk",
            name_en="Junk",
        )
        serializer = ListingWriteSerializer(
            data={
                "brand_id": self.brand.pk,
                "model_id": self.model.pk,
                "city_id": self.city.pk,
                "year": 2020,
                "price": 40_000_000,
                "condition_type": ConditionType.USED,
                "body_type": junk.pk,
                "seller_type": SellerType.PRIVATE,
                "availability": Availability.IN_STOCK,
            },
            context={"request": type("R", (), {"user": self.user})()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("body_type", serializer.errors)

    def test_api_reference_lists_match_canonical_counts(self):
        client = APIClient()
        self.assertEqual(len(client.get("/api/body-types/").json()), len(CANONICAL_BODY_TYPE_SLUGS))
        self.assertEqual(len(client.get("/api/fuel-types/").json()), len(CANONICAL_FUEL_SLUGS))
        self.assertEqual(
            len(client.get("/api/transmissions/").json()),
            len(CANONICAL_TRANSMISSION_SLUGS),
        )
        self.assertEqual(len(client.get("/api/drive-types/").json()), len(CANONICAL_DRIVE_SLUGS))

    def test_api_create_listing_with_canonical_fuel(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(
            "/api/listings/",
            {
                "brand_id": self.brand.pk,
                "model_id": self.model.pk,
                "city_id": self.city.pk,
                "year": 2023,
                "price": 45_000_000,
                "condition_type": ConditionType.USED,
                "fuel": self.petrol.pk,
                "body_type": self.sedan.pk,
                "color": self.color.pk,
                "seller_type": SellerType.PRIVATE,
                "availability": Availability.IN_STOCK,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Listing.objects.filter(
                user=self.user,
                year=2023,
                fuel_id=self.petrol.pk,
                body_type_id=self.sedan.pk,
            ).exists()
        )

    def test_api_list_filter_fuel_query_param(self):
        client = APIClient()
        response = client.get("/api/listings/", {"fuel": self.petrol.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result_ids = {row["id"] for row in response.json()["results"]}
        self.assertIn(self.listing_direct.pk, result_ids)
        self.assertNotIn(self.listing_via_trim.pk, result_ids)
