from django.db import transaction

from .models import SellerProfile, User


def register_user(*, phone: str, password: str, seller_type: str, display_name: str = "") -> User:
    with transaction.atomic():
        user = User.objects.create_user(phone=phone, password=password)
        SellerProfile.objects.create(
            user=user,
            seller_type=seller_type,
            display_name=display_name,
        )
        return user
