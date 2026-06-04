from django.db import models

from core.models import LocalizedNameMixin, SlugMixin
from references.models import BodyType, Country, DriveType, FuelType, TransmissionType


class Brand(LocalizedNameMixin, SlugMixin, models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="brands",
    )
    icon = models.ImageField(upload_to="catalog/brands/", blank=True)

    class Meta:
        ordering = ["name_en"]


class Model(LocalizedNameMixin, SlugMixin, models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="models")

    class Meta:
        ordering = ["name_en"]
        verbose_name = "vehicle model"
        verbose_name_plural = "vehicle models"


class Generation(LocalizedNameMixin, SlugMixin, models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="generations")
    generation_info = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Drom-style label, e.g. «2 поколение, рестайлинг»",
    )
    year_from = models.PositiveSmallIntegerField(null=True, blank=True)
    year_to = models.PositiveSmallIntegerField(null=True, blank=True)
    body_type = models.ForeignKey(
        BodyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generations",
    )
    photo = models.ImageField(upload_to="catalog/generations/", blank=True)

    class Meta:
        ordering = ["-year_from", "name_en"]


class Trim(LocalizedNameMixin, SlugMixin, models.Model):
    generation = models.ForeignKey(
        Generation,
        on_delete=models.CASCADE,
        related_name="trims",
    )
    body_type = models.ForeignKey(
        BodyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trims",
    )
    fuel = models.ForeignKey(
        FuelType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trims",
    )
    transmission = models.ForeignKey(
        TransmissionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trims",
    )
    drive = models.ForeignKey(
        DriveType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trims",
    )

    class Meta:
        ordering = ["name_en"]
