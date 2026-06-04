from django.urls import path

from . import views

urlpatterns = [
    path("countries/", views.CountryListView.as_view(), name="country-list"),
    path("body-types/", views.BodyTypeListView.as_view(), name="body-type-list"),
    path("colors/", views.ColorListView.as_view(), name="color-list"),
    path("fuel-types/", views.FuelTypeListView.as_view(), name="fuel-type-list"),
    path("transmissions/", views.TransmissionTypeListView.as_view(), name="transmission-list"),
    path("drive-types/", views.DriveTypeListView.as_view(), name="drive-type-list"),
]
