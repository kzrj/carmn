from __future__ import annotations

from django.db.models import Max, Min, Q, QuerySet

from listings.models import Listing, ListingPhoto, ListingStatus
from vehicles.models import Generation


def media_url(request, file_field) -> str | None:
    if not file_field:
        return None
    url = file_field.url
    if request is not None:
        return request.build_absolute_uri(url)
    return url


def _listing_scope(qs: QuerySet[Listing], *, dimension: str, group_key: int | None) -> QuerySet[Listing]:
    if group_key is None:
        return qs.none()
    if dimension == "model":
        return qs.filter(model_id=group_key)
    if dimension == "generation":
        return qs.filter(generation_id=group_key)
    return qs.filter(trim_id=group_key)


def sample_photos(
    qs: QuerySet[Listing],
    *,
    dimension: str,
    group_key: int | None,
    request,
    limit: int = 3,
) -> list[str]:
    scoped = _listing_scope(qs, dimension=dimension, group_key=group_key)
    photos: list[str] = []

    if dimension in ("model", "generation", "trim") and group_key:
        generation_qs = Generation.objects.exclude(photo="")
        if dimension == "model":
            generation_qs = generation_qs.filter(model_id=group_key)
        elif dimension == "generation":
            generation_qs = generation_qs.filter(pk=group_key)
        else:
            generation_qs = generation_qs.filter(trims__id=group_key)
        generation = generation_qs.order_by("-year_from").first()
        if generation:
            url = media_url(request, generation.photo)
            if url:
                photos.append(url)

    listing_ids = list(
        scoped.filter(status=ListingStatus.ACTIVE)
        .order_by("-published_at")
        .values_list("pk", flat=True)[:limit * 4]
    )
    if listing_ids:
        seen: set[str] = set(photos)
        for listing_id in listing_ids:
            photo = (
                ListingPhoto.objects.filter(listing_id=listing_id)
                .order_by("-is_primary", "sort_order")
                .first()
            )
            if not photo:
                continue
            url = media_url(request, photo.image)
            if not url or url in seen:
                continue
            seen.add(url)
            photos.append(url)
            if len(photos) >= limit:
                break

    return photos[:limit]


def year_range(qs: QuerySet[Listing], *, dimension: str, group_key: int | None) -> tuple[int | None, int | None]:
    scoped = _listing_scope(qs, dimension=dimension, group_key=group_key)
    bounds = scoped.aggregate(year_min=Min("year"), year_max=Max("year"))
    year_min, year_max = bounds["year_min"], bounds["year_max"]

    if dimension == "model" and group_key:
        gen_bounds = Generation.objects.filter(model_id=group_key).aggregate(
            year_min=Min("year_from"),
            year_max=Max("year_to"),
        )
        if gen_bounds["year_min"] is not None:
            year_min = (
                min(year_min, gen_bounds["year_min"]) if year_min is not None else gen_bounds["year_min"]
            )
        if gen_bounds["year_max"] is not None:
            year_max = (
                max(year_max, gen_bounds["year_max"]) if year_max is not None else gen_bounds["year_max"]
            )

    return year_min, year_max


def specs_summary(qs: QuerySet[Listing], *, dimension: str, group_key: int | None) -> str:
    listing = (
        _listing_scope(qs, dimension=dimension, group_key=group_key)
        .select_related("fuel", "transmission", "drive")
        .order_by("-published_at")
        .first()
    )
    if not listing:
        return ""

    parts: list[str] = []
    if listing.engine_volume:
        parts.append(f"{listing.engine_volume} л")
    if listing.fuel:
        parts.append(listing.fuel.name_ru or listing.fuel.name_en)
    if listing.transmission:
        parts.append(listing.transmission.name_ru or listing.transmission.name_en)
    if listing.drive:
        parts.append(listing.drive.name_ru or listing.drive.name_en)
    return "; ".join(parts)
