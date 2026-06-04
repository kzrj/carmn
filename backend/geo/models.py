from django.db import models

from core.models import LocalizedNameMixin, SlugMixin


class Region(LocalizedNameMixin, SlugMixin, models.Model):
    """Aimag / region."""

    class Meta:
        ordering = ["name_mn"]


class City(LocalizedNameMixin, SlugMixin, models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="cities")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        ordering = ["name_mn"]
        verbose_name_plural = "cities"
