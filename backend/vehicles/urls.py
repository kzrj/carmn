from django.urls import path

from . import views

urlpatterns = [
    path("brands/", views.BrandListView.as_view(), name="brand-list"),
    path("models/", views.ModelListView.as_view(), name="model-list"),
    path("generations/", views.GenerationListView.as_view(), name="generation-list"),
    path("trims/", views.TrimListView.as_view(), name="trim-list"),
]
