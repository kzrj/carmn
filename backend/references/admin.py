from django.contrib import admin

from .models import BodyType, Color, Country, DriveType, FuelType, TransmissionType

for model in (Country, BodyType, Color, FuelType, TransmissionType, DriveType):
    admin.site.register(model)
