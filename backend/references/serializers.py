from rest_framework import serializers

from .models import BodyType, Color, Country, DriveType, FuelType, TransmissionType
from .vehicle_refs import transmission_group


class LocalizedReferenceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        fields = ("id", "slug", "name")

    def get_name(self, obj) -> dict[str, str]:
        return obj.localized_name


class CountrySerializer(LocalizedReferenceSerializer):
    class Meta(LocalizedReferenceSerializer.Meta):
        model = Country
        fields = (*LocalizedReferenceSerializer.Meta.fields, "iso_code")


class BodyTypeSerializer(LocalizedReferenceSerializer):
    class Meta(LocalizedReferenceSerializer.Meta):
        model = BodyType


class ColorSerializer(LocalizedReferenceSerializer):
    class Meta(LocalizedReferenceSerializer.Meta):
        model = Color


class FuelTypeSerializer(LocalizedReferenceSerializer):
    class Meta(LocalizedReferenceSerializer.Meta):
        model = FuelType


class TransmissionTypeSerializer(LocalizedReferenceSerializer):
    group = serializers.SerializerMethodField()

    class Meta(LocalizedReferenceSerializer.Meta):
        model = TransmissionType
        fields = (*LocalizedReferenceSerializer.Meta.fields, "group")

    def get_group(self, obj) -> str | None:
        return transmission_group(obj.slug)


class DriveTypeSerializer(LocalizedReferenceSerializer):
    class Meta(LocalizedReferenceSerializer.Meta):
        model = DriveType
