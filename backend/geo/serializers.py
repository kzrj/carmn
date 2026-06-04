from rest_framework import serializers

from .models import City, Region


class RegionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ("id", "slug", "name")

    def get_name(self, obj: Region) -> dict[str, str]:
        return obj.localized_name


class CitySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    region = RegionSerializer(read_only=True)
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(), source="region", write_only=True
    )

    class Meta:
        model = City
        fields = (
            "id",
            "slug",
            "name",
            "region",
            "region_id",
            "latitude",
            "longitude",
        )

    def get_name(self, obj: City) -> dict[str, str]:
        return obj.localized_name
