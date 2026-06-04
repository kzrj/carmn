from __future__ import annotations

from typing import Any

from django.core.paginator import Paginator
from django.db.models import Count, Max, Min, QuerySet

from listings.grouping_media import sample_photos, specs_summary, year_range
from vehicles.models import Generation, Model, Trim
from vehicles.serializers import BrandSerializer, GenerationSerializer, ModelSerializer, TrimSerializer


def resolve_listing_group_dimension(params: dict[str, Any]) -> str | None:
    """Next drill-down level for «model lineup» (Drom «Модельный ряд»)."""
    if params.get("trim"):
        return None
    if params.get("generation"):
        return "trim"
    if params.get("model"):
        return "generation"
    return "model"


def _order_groups(qs: QuerySet, dimension: str, ordering: str) -> QuerySet:
    name_field = {
        "model": "model__name_ru",
        "generation": "generation__name_ru",
        "trim": "trim__name_ru",
    }[dimension]

    if ordering == "count":
        return qs.order_by("count", name_field)
    if ordering == "name":
        return qs.order_by(name_field, "-count")
    return qs.order_by("-count", name_field)


def aggregate_listing_groups(
    qs: QuerySet,
    *,
    dimension: str,
    ordering: str = "-count",
) -> QuerySet:
    group_id_field = {
        "model": "model_id",
        "generation": "generation_id",
        "trim": "trim_id",
    }[dimension]

    grouped = (
        qs.values(group_id_field)
        .annotate(
            count=Count("pk"),
            min_price=Min("price"),
            max_price=Max("price"),
        )
        .filter(count__gt=0)
    )
    return _order_groups(grouped, dimension, ordering)


def paginate_groups(grouped_qs: QuerySet, *, page: int, page_size: int) -> tuple[list[dict], int]:
    paginator = Paginator(grouped_qs, page_size)
    page_obj = paginator.get_page(page)
    return list(page_obj.object_list), paginator.count


def count_listing_groups(qs: QuerySet, *, dimension: str) -> int:
    return aggregate_listing_groups(qs, dimension=dimension).count()


def _group_key(row: dict, dimension: str) -> int | None:
    field = {"model": "model_id", "generation": "generation_id", "trim": "trim_id"}[dimension]
    return row.get(field)


def serialize_listing_groups(
    rows: list[dict],
    *,
    dimension: str,
    request,
    listings_qs: QuerySet | None = None,
    fallback_model_id: int | None = None,
    fallback_generation_id: int | None = None,
) -> list[dict]:
    if not rows:
        return []

    if dimension == "model":
        model_ids = [row["model_id"] for row in rows if row.get("model_id")]
        models = {
            m.id: m
            for m in Model.objects.filter(id__in=model_ids).select_related("brand", "brand__country")
        }
        out = []
        for row in rows:
            model = models.get(row.get("model_id"))
            if not model:
                continue
            out.append(
                _serialize_group_row(
                    row,
                    brand=model.brand,
                    model=model,
                    request=request,
                    dimension=dimension,
                    listings_qs=listings_qs,
                )
            )
        return out

    if dimension == "generation":
        generation_ids = [row["generation_id"] for row in rows if row.get("generation_id")]
        generations = {
            g.id: g
            for g in Generation.objects.filter(id__in=generation_ids)
            .select_related("model", "model__brand", "model__brand__country", "body_type")
        }
        model_ids = {g.model_id for g in generations.values()}
        if fallback_model_id:
            model_ids.add(fallback_model_id)
        models = {m.id: m for m in Model.objects.filter(id__in=model_ids).select_related("brand", "brand__country")}
        fallback_model = models.get(fallback_model_id) if fallback_model_id else None
        out = []
        for row in rows:
            generation = generations.get(row.get("generation_id"))
            model = generation.model if generation else fallback_model
            if not model:
                continue
            out.append(
                _serialize_group_row(
                    row,
                    brand=model.brand,
                    model=model,
                    generation=generation,
                    request=request,
                    dimension=dimension,
                    listings_qs=listings_qs,
                )
            )
        return out

    trim_ids = [row["trim_id"] for row in rows if row.get("trim_id")]
    trims = {
        t.id: t
        for t in Trim.objects.filter(id__in=trim_ids)
        .select_related(
            "generation",
            "generation__model",
            "generation__model__brand",
            "generation__model__brand__country",
            "body_type",
            "fuel",
            "transmission",
            "drive",
        )
    }
    fallback_generation = None
    if fallback_generation_id:
        fallback_generation = (
            Generation.objects.filter(pk=fallback_generation_id)
            .select_related("model", "model__brand", "model__brand__country", "body_type")
            .first()
        )
    out = []
    for row in rows:
        trim = trims.get(row.get("trim_id"))
        generation = trim.generation if trim else fallback_generation
        if not generation:
            continue
        model = generation.model
        out.append(
            _serialize_group_row(
                row,
                brand=model.brand,
                model=model,
                generation=generation,
                trim=trim,
                request=request,
                dimension=dimension,
                listings_qs=listings_qs,
            )
        )
    return out


def _serialize_group_row(
    row: dict,
    *,
    brand,
    model,
    generation=None,
    trim=None,
    request,
    dimension: str,
    listings_qs: QuerySet | None = None,
) -> dict:
    ctx = {"request": request}
    group_key = _group_key(row, dimension)
    year_from, year_to = (None, None)
    photos: list[str] = []
    specs = ""
    if listings_qs is not None:
        year_from, year_to = year_range(listings_qs, dimension=dimension, group_key=group_key)
        photos = sample_photos(listings_qs, dimension=dimension, group_key=group_key, request=request)
        specs = specs_summary(listings_qs, dimension=dimension, group_key=group_key)

    return {
        "count": row["count"],
        "min_price": row["min_price"],
        "max_price": row["max_price"],
        "year_from": year_from,
        "year_to": year_to,
        "photos": photos,
        "specs_summary": specs,
        "brand": BrandSerializer(brand, context=ctx).data,
        "model": ModelSerializer(model, context=ctx).data,
        "generation": GenerationSerializer(generation, context=ctx).data if generation else None,
        "trim": TrimSerializer(trim, context=ctx).data if trim else None,
    }
