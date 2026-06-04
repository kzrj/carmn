from rest_framework import generics

from .models import Brand, Generation, Model, Trim
from .serializers import BrandSerializer, GenerationSerializer, ModelSerializer, TrimSerializer


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.select_related("country")
    serializer_class = BrandSerializer


class ModelListView(generics.ListAPIView):
    serializer_class = ModelSerializer

    def get_queryset(self):
        qs = Model.objects.all()
        brand_id = self.request.query_params.get("brand")
        if brand_id:
            qs = qs.filter(brand_id=brand_id)
        return qs


class GenerationListView(generics.ListAPIView):
    serializer_class = GenerationSerializer

    def get_queryset(self):
        qs = Generation.objects.select_related("body_type")
        model_id = self.request.query_params.get("model")
        body_type_id = self.request.query_params.get("body_type")
        if model_id:
            qs = qs.filter(model_id=model_id)
        if body_type_id:
            qs = qs.filter(body_type_id=body_type_id)
        return qs


class TrimListView(generics.ListAPIView):
    serializer_class = TrimSerializer

    def get_queryset(self):
        qs = Trim.objects.select_related(
            "generation",
            "body_type",
            "fuel",
            "transmission",
            "drive",
        )
        generation_id = self.request.query_params.get("generation")
        model_id = self.request.query_params.get("model")
        body_type_id = self.request.query_params.get("body_type")
        if generation_id:
            qs = qs.filter(generation_id=generation_id)
        if model_id:
            qs = qs.filter(generation__model_id=model_id)
        if body_type_id:
            qs = qs.filter(body_type_id=body_type_id)
        return qs
