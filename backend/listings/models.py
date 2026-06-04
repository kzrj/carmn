from django.conf import settings
from django.db import models
from django.db.models import Q

from geo.models import City
from references.models import BodyType, Color, Country, DriveType, FuelType, TransmissionType
from users.models import SellerType
from vehicles.models import Brand, Generation, Model, Trim


class ListingStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SOLD = "sold", "Sold"
    MODERATION = "moderation", "Moderation"
    ARCHIVED = "archived", "Archived"


class ListingSource(models.TextChoices):
    USER = "user", "User"
    UNEGUI = "unegui", "Unegui"
    FACEBOOK = "facebook", "Facebook"
    DEALER = "dealer", "Dealer"


class ConditionType(models.TextChoices):
    NEW = "new", "New"
    USED = "used", "Used"


class Steering(models.TextChoices):
    LEFT = "left", "Left"
    RIGHT = "right", "Right"


class PtsStatus(models.TextChoices):
    ANY = "any", "Any"
    OK = "ok", "In order"
    PROBLEM = "problem", "Missing or problematic"


class DamageStatus(models.TextChoices):
    ANY = "any", "Any"
    OK = "ok", "No repair needed"
    REPAIR = "repair", "Needs repair or not running"


class Availability(models.TextChoices):
    IN_STOCK = "in_stock", "In stock"
    IN_TRANSIT = "in_transit", "In transit"
    ON_ORDER = "on_order", "On order"


class OwnersCount(models.TextChoices):
    ANY = "any", "Any"
    ONE = "one", "One"
    UP_TO_TWO = "up_to_two", "Up to two"
    UP_TO_THREE = "up_to_three", "Up to three"


class Listing(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="listings")
    model = models.ForeignKey(Model, on_delete=models.PROTECT, related_name="listings")
    generation = models.ForeignKey(
        Generation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
    )
    trim = models.ForeignKey(
        Trim,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
    )

    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="listings")

    year = models.PositiveSmallIntegerField()
    price = models.PositiveBigIntegerField(help_text="Price in MNT")
    price_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price in USD, if specified",
    )
    mileage = models.PositiveIntegerField(null=True, blank=True, help_text="km")

    condition_type = models.CharField(max_length=10, choices=ConditionType.choices)
    status = models.CharField(
        max_length=12,
        choices=ListingStatus.choices,
        default=ListingStatus.ACTIVE,
    )
    source = models.CharField(
        max_length=20,
        choices=ListingSource.choices,
        default=ListingSource.USER,
    )
    external_id = models.CharField(max_length=255, blank=True, default="")
    external_url = models.URLField(blank=True, default="")
    parsed_at = models.DateTimeField(null=True, blank=True)

    vin = models.CharField(max_length=17, blank=True, default="", db_index=True)
    chassis_number = models.CharField(max_length=30, blank=True, default="")

    view_count = models.PositiveIntegerField(default=0)

    body_type = models.ForeignKey(
        BodyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
    )
    fuel = models.ForeignKey(
        FuelType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
    )
    transmission = models.ForeignKey(
        TransmissionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
    )
    drive = models.ForeignKey(
        DriveType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
    )

    engine_volume = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="liters",
    )
    power_hp = models.PositiveSmallIntegerField(null=True, blank=True)

    steering = models.CharField(
        max_length=10,
        choices=Steering.choices,
        default=Steering.LEFT,
    )
    pts_status = models.CharField(
        max_length=10,
        choices=PtsStatus.choices,
        default=PtsStatus.OK,
    )
    damage_status = models.CharField(
        max_length=10,
        choices=DamageStatus.choices,
        default=DamageStatus.OK,
    )
    seller_type = models.CharField(max_length=20, choices=SellerType.choices)
    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.IN_STOCK,
    )
    owners_count = models.CharField(
        max_length=20,
        choices=[
            (OwnersCount.ONE, OwnersCount.ONE.label),
            (OwnersCount.UP_TO_TWO, OwnersCount.UP_TO_TWO.label),
            (OwnersCount.UP_TO_THREE, OwnersCount.UP_TO_THREE.label),
        ],
        null=True,
        blank=True,
    )

    exchange_possible = models.BooleanField(default=False)
    is_certified = models.BooleanField(default=False)
    without_local_mileage = models.BooleanField(
        default=False,
        help_text="Not registered in Mongolia / freshly imported",
    )
    customs_cleared = models.BooleanField(default=True)
    import_country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imported_listings",
    )

    description = models.TextField(blank=True, default="")

    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["brand", "model", "year"]),
            models.Index(fields=["price"]),
            models.Index(fields=["city"]),
            models.Index(fields=["-view_count"]),
            models.Index(fields=["source"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"],
                condition=~Q(external_id=""),
                name="uniq_listing_source_external_id",
            ),
            models.UniqueConstraint(
                fields=["vin"],
                condition=~Q(vin=""),
                name="uniq_listing_vin_nonempty",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.brand} {self.model} {self.year}"


class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="listings/%Y/%m/")
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "id"]


class ListingPriceHistory(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="price_history")
    old_price = models.PositiveBigIntegerField()
    new_price = models.PositiveBigIntegerField()
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listing_price_changes",
    )

    class Meta:
        ordering = ["-changed_at"]
        verbose_name_plural = "listing price histories"


class UserFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_listings",
    )
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "listing"], name="uniq_user_favorite_listing"),
        ]


class ListingView(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listing_views",
    )
    ip_hash = models.CharField(max_length=64, blank=True, default="")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(fields=["listing", "-viewed_at"]),
            models.Index(fields=["listing", "ip_hash", "-viewed_at"]),
        ]
