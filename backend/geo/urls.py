from django.urls import path

from . import views

urlpatterns = [
    path("regions/", views.RegionListView.as_view(), name="region-list"),
    path("cities/", views.CityListView.as_view(), name="city-list"),
]
