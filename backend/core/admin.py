from django.contrib import admin

from core.models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("currency", "rate_to_mnt", "date")
    list_filter = ("currency",)
    ordering = ("-date", "currency")
