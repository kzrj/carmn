from django.contrib import admin

from .models import SellerProfile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone", "is_staff", "is_active", "date_joined")
    search_fields = ("phone",)


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "seller_type", "display_name", "company_name")
    list_filter = ("seller_type",)
