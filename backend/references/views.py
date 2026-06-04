from rest_framework import generics

from .body_types import filter_body_types_queryset
from .models import BodyType, Color, Country, DriveType, FuelType, TransmissionType
from .vehicle_refs import (
    filter_drive_types_queryset,
    filter_fuel_types_queryset,
    filter_transmissions_queryset,
)
from .serializers import (
    BodyTypeSerializer,
    ColorSerializer,
    CountrySerializer,
    DriveTypeSerializer,
    FuelTypeSerializer,
    TransmissionTypeSerializer,
)


class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class BodyTypeListView(generics.ListAPIView):
    serializer_class = BodyTypeSerializer

    def get_queryset(self):
        return filter_body_types_queryset(BodyType.objects.all())


class ColorListView(generics.ListAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class FuelTypeListView(generics.ListAPIView):
    serializer_class = FuelTypeSerializer

    def get_queryset(self):
        return filter_fuel_types_queryset(FuelType.objects.all())


class TransmissionTypeListView(generics.ListAPIView):
    serializer_class = TransmissionTypeSerializer

    def get_queryset(self):
        return filter_transmissions_queryset(TransmissionType.objects.all())


class DriveTypeListView(generics.ListAPIView):
    serializer_class = DriveTypeSerializer

    def get_queryset(self):
        return filter_drive_types_queryset(DriveType.objects.all())
