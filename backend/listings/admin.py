from django.contrib import admin

from .models import (
    Listing,
    ListingPhoto,
    ListingPriceHistory,
    ListingView,
    UserFavorite,
)


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 0


class ListingPriceHistoryInline(admin.TabularInline):
    model = ListingPriceHistory
    extra = 0
    readonly_fields = ("old_price", "new_price", "changed_at", "changed_by")
    can_delete = False


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "brand",
        "model",
        "year",
        "price",
        "price_usd",
        "city",
        "status",
        "source",
        "view_count",
        "published_at",
    )
    list_filter = ("status", "source", "condition_type", "city__region", "brand")
    search_fields = ("description", "brand__name_en", "model__name_en", "vin", "chassis_number", "external_id")
    inlines = [ListingPhotoInline, ListingPriceHistoryInline]
    raw_id_fields = ("user", "brand", "model", "generation", "trim", "city")


@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ("listing", "sort_order", "is_primary")


@admin.register(ListingPriceHistory)
class ListingPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("listing", "old_price", "new_price", "changed_at", "changed_by")
    raw_id_fields = ("listing", "changed_by")


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "created_at")
    raw_id_fields = ("user", "listing")


@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    list_display = ("listing", "user", "ip_hash", "viewed_at")
    raw_id_fields = ("listing", "user")
