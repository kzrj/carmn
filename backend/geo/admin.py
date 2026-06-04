from django.contrib import admin

from .models import City, Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name_mn", "name_ru", "slug")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name_mn", "region", "latitude", "longitude")
    list_filter = ("region",)
    prepopulated_fields = {"slug": ("name_en",)}
