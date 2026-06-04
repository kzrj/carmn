from django.db import models

from core.models import LocalizedNameMixin, SlugMixin


class Country(LocalizedNameMixin, SlugMixin, models.Model):
    """Country of brand origin or vehicle import."""

    iso_code = models.CharField(max_length=3, blank=True, default="")

    class Meta:
        ordering = ["name_en"]
        verbose_name_plural = "countries"


class BodyType(LocalizedNameMixin, SlugMixin, models.Model):
    class Meta:
        ordering = ["name_en"]


class Color(LocalizedNameMixin, SlugMixin, models.Model):
    class Meta:
        ordering = ["name_en"]


class FuelType(LocalizedNameMixin, SlugMixin, models.Model):
    class Meta:
        ordering = ["name_en"]


class TransmissionType(LocalizedNameMixin, SlugMixin, models.Model):
    class Meta:
        ordering = ["name_en"]


class DriveType(LocalizedNameMixin, SlugMixin, models.Model):
    class Meta:
        ordering = ["name_en"]
