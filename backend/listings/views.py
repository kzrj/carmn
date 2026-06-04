from django.conf import settings
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from listings.filters import ListingFilter
from listings.grouping import (
    aggregate_listing_groups,
    count_listing_groups,
    paginate_groups,
    resolve_listing_group_dimension,
    serialize_listing_groups,
)
from listings.models import Listing, ListingPhoto, ListingStatus, UserFavorite
from listings.services import add_favorite, record_listing_view, remove_favorite, search_listings

from .serializers import (
    ListingDetailSerializer,
    ListingListSerializer,
    ListingPhotoSerializer,
    ListingWriteSerializer,
)


class ListingListCreateView(generics.ListCreateAPIView):
    filterset_class = ListingFilter
    ordering = ["-published_at"]

    def get_queryset(self):
        return search_listings(
            Listing.objects.filter(status=ListingStatus.ACTIVE),
            user=self.request.user,
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        dimension = resolve_listing_group_dimension(request.query_params)
        if dimension is not None:
            filterset = ListingFilter(request.query_params, queryset=self.get_queryset())
            if filterset.is_valid():
                response.data["model_groups_count"] = count_listing_groups(filterset.qs, dimension=dimension)
        return response

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ListingWriteSerializer
        return ListingListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class ListingDetailView(generics.RetrieveUpdateAPIView):
    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ListingWriteSerializer
        return ListingDetailSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = search_listings(Listing.objects.all(), user=self.request.user)
        if self.request.method == "GET":
            qs = qs.prefetch_related("price_history")
            user = self.request.user
            if user.is_authenticated:
                return qs.filter(Q(status=ListingStatus.ACTIVE) | Q(user=user))
            return qs.filter(status=ListingStatus.ACTIVE)
        return qs.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == ListingStatus.ACTIVE:
            record_listing_view(listing=instance, request=request, user=request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ListingPhotoUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk: int):
        listing = Listing.objects.filter(pk=pk, user=request.user).first()
        if not listing:
            return Response(status=status.HTTP_404_NOT_FOUND)

        image = request.FILES.get("image")
        if not image:
            return Response({"detail": "image is required"}, status=status.HTTP_400_BAD_REQUEST)

        is_primary = not listing.photos.exists()
        photo = ListingPhoto.objects.create(
            listing=listing,
            image=image,
            sort_order=listing.photos.count(),
            is_primary=is_primary,
        )
        return Response(ListingPhotoSerializer(photo, context={"request": request}).data, status=201)


class ListingMarkSoldView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        listing = Listing.objects.filter(pk=pk, user=request.user).first()
        if not listing:
            return Response(status=status.HTTP_404_NOT_FOUND)
        listing.status = ListingStatus.SOLD
        listing.save(update_fields=["status", "updated_at"])
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)


class ListingArchiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        listing = Listing.objects.filter(pk=pk, user=request.user).first()
        if not listing:
            return Response(status=status.HTTP_404_NOT_FOUND)
        listing.status = ListingStatus.ARCHIVED
        listing.save(update_fields=["status", "updated_at"])
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)


class ListingFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        listing = Listing.objects.filter(pk=pk, status=ListingStatus.ACTIVE).first()
        if not listing:
            return Response(status=status.HTTP_404_NOT_FOUND)
        add_favorite(user=request.user, listing=listing)
        return Response({"is_favorited": True}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk: int):
        listing = Listing.objects.filter(pk=pk).first()
        if not listing:
            return Response(status=status.HTTP_404_NOT_FOUND)
        remove_favorite(user=request.user, listing=listing)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListingModelGroupsView(APIView):
    """«Модельный ряд»: группировка объявлений по model / generation / trim."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        dimension = resolve_listing_group_dimension(request.query_params)
        if dimension is None:
            return Response(
                {"detail": "Model groups are not available at this filter depth."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        base_qs = search_listings(
            Listing.objects.filter(status=ListingStatus.ACTIVE),
            user=request.user,
        )
        filterset = ListingFilter(request.query_params, queryset=base_qs)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        ordering = request.query_params.get("groups_ordering", "-count")
        if ordering not in ("-count", "count", "name"):
            ordering = "-count"

        grouped_qs = aggregate_listing_groups(filterset.qs, dimension=dimension, ordering=ordering)
        try:
            page = max(1, int(request.query_params.get("page", 1)))
        except (TypeError, ValueError):
            page = 1

        page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", 20)
        rows, total = paginate_groups(grouped_qs, page=page, page_size=page_size)
        params = request.query_params
        fallback_model_id = int(params["model"]) if params.get("model") else None
        fallback_generation_id = int(params["generation"]) if params.get("generation") else None
        results = serialize_listing_groups(
            rows,
            dimension=dimension,
            request=request,
            listings_qs=filterset.qs,
            fallback_model_id=fallback_model_id,
            fallback_generation_id=fallback_generation_id,
        )

        return Response(
            {
                "count": total,
                "listings_count": filterset.qs.count(),
                "dimension": dimension,
                "results": results,
            }
        )


class ListingFavoritesListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListingListSerializer

    def get_queryset(self):
        listing_ids = UserFavorite.objects.filter(user=self.request.user).values_list("listing_id", flat=True)
        return search_listings(
            Listing.objects.filter(pk__in=listing_ids, status=ListingStatus.ACTIVE),
            user=self.request.user,
        )


class VinLookupView(APIView):
    """Stub for future VIN decode / autofill integration."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(
            {"detail": "VIN lookup is not available yet."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
