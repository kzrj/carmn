from rest_framework import serializers

from .models import SellerProfile, SellerType, User


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ("seller_type", "display_name", "company_name")


class UserSerializer(serializers.ModelSerializer):
    seller_profile = SellerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "phone", "date_joined", "seller_profile")


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(min_length=6, write_only=True)
    seller_type = serializers.ChoiceField(choices=SellerType.choices, default=SellerType.PRIVATE)
    display_name = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")

    def validate_phone(self, value: str) -> str:
        phone = User.objects.normalize_phone(value)
        if User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("User with this phone already exists.")
        return phone
