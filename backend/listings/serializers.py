from rest_framework import serializers



from geo.serializers import CitySerializer

from geo.models import City

from references.canonical import (
    canonical_body_types,
    canonical_drive_types,
    canonical_fuel_types,
    canonical_transmissions,
)
from references.serializers import (

    BodyTypeSerializer,

    ColorSerializer,

    CountrySerializer,

    DriveTypeSerializer,

    FuelTypeSerializer,

    TransmissionTypeSerializer,

)

from users.serializers import UserSerializer

from vehicles.models import Brand, Generation, Model, Trim

from vehicles.serializers import BrandSerializer, GenerationSerializer, ModelSerializer, TrimSerializer



from .models import Listing, ListingPhoto, ListingPriceHistory

from .services import normalize_vin





class RelativeImageField(serializers.ImageField):
    """Return /media/... path so browser uses the same origin (nginx :8082)."""

    def to_representation(self, value):
        if not value:
            return None
        return value.url


class ListingPhotoSerializer(serializers.ModelSerializer):
    image = RelativeImageField(read_only=True)

    class Meta:

        model = ListingPhoto

        fields = ("id", "image", "sort_order", "is_primary")

        read_only_fields = ("id",)





class ListingPriceHistorySerializer(serializers.ModelSerializer):

    class Meta:

        model = ListingPriceHistory

        fields = ("id", "old_price", "new_price", "changed_at")

        read_only_fields = fields





class ListingListSerializer(serializers.ModelSerializer):

    brand = BrandSerializer(read_only=True)

    model = ModelSerializer(read_only=True)

    city = CitySerializer(read_only=True)

    primary_photo = serializers.SerializerMethodField()

    has_photos = serializers.SerializerMethodField()

    is_favorited = serializers.SerializerMethodField()



    class Meta:

        model = Listing

        fields = (

            "id",

            "brand",

            "model",

            "year",

            "price",

            "price_usd",

            "mileage",

            "condition_type",

            "status",

            "source",

            "city",

            "seller_type",

            "steering",

            "view_count",

            "published_at",

            "primary_photo",

            "has_photos",

            "is_favorited",

        )



    def get_primary_photo(self, obj: Listing) -> str | None:

        photo = next((p for p in obj.photos.all() if p.is_primary), None)

        if not photo:

            photo = obj.photos.first()

        if photo and photo.image:
            return photo.image.url
        return None



    def get_has_photos(self, obj: Listing) -> bool:

        return obj.photos.exists()



    def get_is_favorited(self, obj: Listing) -> bool:

        if hasattr(obj, "_is_favorited"):

            return bool(obj._is_favorited)

        request = self.context.get("request")

        if not request or not request.user.is_authenticated:

            return False

        return obj.favorited_by.filter(user_id=request.user.id).exists()





class ListingDetailSerializer(ListingListSerializer):

    generation = GenerationSerializer(read_only=True)

    trim = TrimSerializer(read_only=True)

    body_type = BodyTypeSerializer(read_only=True)

    color = ColorSerializer(read_only=True)

    fuel = FuelTypeSerializer(read_only=True)

    transmission = TransmissionTypeSerializer(read_only=True)

    drive = DriveTypeSerializer(read_only=True)

    import_country = CountrySerializer(read_only=True)

    photos = ListingPhotoSerializer(many=True, read_only=True)

    price_history = ListingPriceHistorySerializer(many=True, read_only=True)

    user = UserSerializer(read_only=True)



    class Meta(ListingListSerializer.Meta):

        fields = ListingListSerializer.Meta.fields + (

            "generation",

            "trim",

            "body_type",

            "color",

            "fuel",

            "transmission",

            "drive",

            "engine_volume",

            "power_hp",

            "pts_status",

            "damage_status",

            "availability",

            "owners_count",

            "exchange_possible",

            "is_certified",

            "without_local_mileage",

            "customs_cleared",

            "import_country",

            "vin",

            "chassis_number",

            "external_url",

            "parsed_at",

            "description",

            "updated_at",

            "photos",

            "price_history",

            "user",

        )





class ListingWriteSerializer(serializers.ModelSerializer):

    brand_id = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), source="brand")

    model_id = serializers.PrimaryKeyRelatedField(queryset=Model.objects.all(), source="model")

    generation_id = serializers.PrimaryKeyRelatedField(

        queryset=Generation.objects.all(), source="generation", required=False, allow_null=True

    )

    trim_id = serializers.PrimaryKeyRelatedField(

        queryset=Trim.objects.all(), source="trim", required=False, allow_null=True

    )

    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), source="city")

    body_type = serializers.PrimaryKeyRelatedField(
        queryset=canonical_body_types(),
        required=False,
        allow_null=True,
    )
    fuel = serializers.PrimaryKeyRelatedField(
        queryset=canonical_fuel_types(),
        required=False,
        allow_null=True,
    )
    transmission = serializers.PrimaryKeyRelatedField(
        queryset=canonical_transmissions(),
        required=False,
        allow_null=True,
    )
    drive = serializers.PrimaryKeyRelatedField(
        queryset=canonical_drive_types(),
        required=False,
        allow_null=True,
    )



    class Meta:

        model = Listing

        fields = (

            "brand_id",

            "model_id",

            "generation_id",

            "trim_id",

            "city_id",

            "year",

            "price",

            "price_usd",

            "mileage",

            "condition_type",

            "body_type",

            "color",

            "fuel",

            "transmission",

            "drive",

            "engine_volume",

            "power_hp",

            "steering",

            "pts_status",

            "damage_status",

            "seller_type",

            "availability",

            "owners_count",

            "exchange_possible",

            "is_certified",

            "without_local_mileage",

            "customs_cleared",

            "import_country",

            "vin",

            "chassis_number",

            "description",

        )



    def validate_vin(self, value: str) -> str:

        vin = normalize_vin(value)

        if not vin:

            return ""

        if len(vin) != 17:

            raise serializers.ValidationError("VIN must be exactly 17 characters.")

        invalid_chars = set("IOQ")

        if not vin.isalnum() or any(char in invalid_chars for char in vin):

            raise serializers.ValidationError("VIN contains invalid characters.")

        return vin



    def validate(self, attrs):

        from django.core.exceptions import ValidationError as DjangoValidationError

        from listings.services import validate_vehicle_tree



        price = attrs.get("price")

        price_usd = attrs.get("price_usd")

        if self.instance is None and not price and not price_usd:

            raise serializers.ValidationError("Either price or price_usd is required.")



        try:

            validate_vehicle_tree(

                brand=attrs.get("brand", self.instance.brand if self.instance else None),

                model=attrs.get("model", self.instance.model if self.instance else None),

                generation=attrs.get("generation", self.instance.generation if self.instance else None),

                trim=attrs.get("trim", self.instance.trim if self.instance else None),

            )

        except DjangoValidationError as exc:

            raise serializers.ValidationError(exc.messages) from exc

        return attrs



    def create(self, validated_data):

        from listings.services import create_listing



        user = self.context["request"].user

        return create_listing(user=user, data=validated_data)



    def update(self, instance, validated_data):

        from listings.services import update_listing



        user = self.context["request"].user

        return update_listing(listing=instance, data=validated_data, changed_by=user)


