from django.urls import path



from . import views



urlpatterns = [

    path("listings/", views.ListingListCreateView.as_view(), name="listing-list"),

    path("listings/model-groups/", views.ListingModelGroupsView.as_view(), name="listing-model-groups"),

    path("listings/favorites/", views.ListingFavoritesListView.as_view(), name="listing-favorites"),

    path("listings/<int:pk>/", views.ListingDetailView.as_view(), name="listing-detail"),

    path("listings/<int:pk>/photos/", views.ListingPhotoUploadView.as_view(), name="listing-photo"),

    path("listings/<int:pk>/sold/", views.ListingMarkSoldView.as_view(), name="listing-sold"),

    path("listings/<int:pk>/archive/", views.ListingArchiveView.as_view(), name="listing-archive"),

    path("listings/<int:pk>/favorite/", views.ListingFavoriteView.as_view(), name="listing-favorite"),

    path("vin/lookup/", views.VinLookupView.as_view(), name="vin-lookup"),

]

