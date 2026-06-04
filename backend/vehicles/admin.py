from django.contrib import admin
from django.utils.html import format_html

from .models import Brand, Generation, Model, Trim


class ModelInline(admin.TabularInline):
    model = Model
    extra = 0


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_mn", "country", "slug", "has_icon")
    list_filter = ("country",)
    inlines = [ModelInline]
    prepopulated_fields = {"slug": ("name_en",)}
    readonly_fields = ("icon_preview",)

    @admin.display(boolean=True, description="Icon")
    def has_icon(self, obj: Brand) -> bool:
        return bool(obj.icon)

    @admin.display(description="Preview")
    def icon_preview(self, obj: Brand) -> str:
        if not obj.icon:
            return "—"
        return format_html('<img src="{}" style="max-height:48px">', obj.icon.url)


class GenerationInline(admin.TabularInline):
    model = Generation
    extra = 0


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("name_en", "brand", "slug")
    list_filter = ("brand",)
    inlines = [GenerationInline]
    prepopulated_fields = {"slug": ("name_en",)}


class TrimInline(admin.TabularInline):
    model = Trim
    extra = 0


@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = ("name_en", "model", "year_from", "year_to", "body_type", "has_photo")
    list_filter = ("model__brand", "body_type")
    inlines = [TrimInline]
    prepopulated_fields = {"slug": ("name_en",)}
    readonly_fields = ("photo_preview",)

    @admin.display(boolean=True, description="Photo")
    def has_photo(self, obj: Generation) -> bool:
        return bool(obj.photo)

    @admin.display(description="Preview")
    def photo_preview(self, obj: Generation) -> str:
        if not obj.photo:
            return "—"
        return format_html('<img src="{}" style="max-height:120px">', obj.photo.url)


@admin.register(Trim)
class TrimAdmin(admin.ModelAdmin):
    list_display = ("name_en", "generation", "body_type", "fuel", "transmission", "drive", "slug")
    list_filter = ("generation__model__brand", "body_type", "fuel", "transmission", "drive")
    prepopulated_fields = {"slug": ("name_en",)}
