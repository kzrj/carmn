from django.db import models


class LocalizedNameMixin(models.Model):
    name_mn = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255, blank=True, default="")
    name_en = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name_mn or self.name_ru or self.name_en

    @property
    def localized_name(self) -> dict[str, str]:
        return {"mn": self.name_mn, "ru": self.name_ru, "en": self.name_en}


class SlugMixin(models.Model):
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        abstract = True


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, default="USD")
    rate_to_mnt = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()

    class Meta:
        ordering = ["-date", "currency"]
        constraints = [
            models.UniqueConstraint(fields=["currency", "date"], name="uniq_exchange_rate_currency_date"),
        ]

    def __str__(self) -> str:
        return f"{self.currency} @ {self.date}: {self.rate_to_mnt} MNT"
