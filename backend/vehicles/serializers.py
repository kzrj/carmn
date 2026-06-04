from rest_framework import serializers

from references.serializers import BodyTypeSerializer, CountrySerializer, DriveTypeSerializer, FuelTypeSerializer, TransmissionTypeSerializer

from .models import Brand, Generation, Model, Trim


class BrandSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    country = CountrySerializer(read_only=True)
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ("id", "slug", "name", "country", "icon")

    def get_name(self, obj: Brand) -> dict[str, str]:
        return obj.localized_name

    def get_icon(self, obj: Brand) -> str | None:
        if not obj.icon:
            return None
        request = self.context.get("request")
        url = obj.icon.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class ModelSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Model
        fields = ("id", "slug", "name", "brand_id")

    def get_name(self, obj: Model) -> dict[str, str]:
        return obj.localized_name


class GenerationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    body_type = BodyTypeSerializer(read_only=True)
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Generation
        fields = (
            "id",
            "slug",
            "name",
            "generation_info",
            "model_id",
            "year_from",
            "year_to",
            "body_type_id",
            "body_type",
            "photo",
        )

    def get_name(self, obj: Generation) -> dict[str, str]:
        return obj.localized_name

    def get_photo(self, obj: Generation) -> str | None:
        if obj.photo:
            return obj.photo.url
        return None


class TrimSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    body_type = BodyTypeSerializer(read_only=True)
    fuel = FuelTypeSerializer(read_only=True)
    transmission = TransmissionTypeSerializer(read_only=True)
    drive = DriveTypeSerializer(read_only=True)

    class Meta:
        model = Trim
        fields = (
            "id",
            "slug",
            "name",
            "generation_id",
            "body_type_id",
            "body_type",
            "fuel_id",
            "fuel",
            "transmission_id",
            "transmission",
            "drive_id",
            "drive",
        )

    def get_name(self, obj: Trim) -> dict[str, str]:
        return obj.localized_name
