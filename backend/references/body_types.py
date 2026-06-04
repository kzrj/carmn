from __future__ import annotations

import re

from django.db.models import Case, IntegerField, Q, QuerySet, When

from references.models import BodyType

# Drom auto.drom.ru filter body types (order preserved for UI).
CANONICAL_BODY_TYPES: tuple[tuple[str, str, str, str], ...] = (
    ("sedan", "Седан", "Седан", "Sedan"),
    ("hatchback-5d", "Хэтчбек 5 дв.", "Хэтчбек 5 дв.", "Hatchback 5-door"),
    ("hatchback-3d", "Хэтчбек 3 дв.", "Хэтчбек 3 дв.", "Hatchback 3-door"),
    ("liftback", "Лифтбек", "Лифтбек", "Liftback"),
    ("suv-5d", "Джип 5 дв.", "Джип 5 дв.", "SUV 5-door"),
    ("suv-3d", "Джип 3 дв.", "Джип 3 дв.", "SUV 3-door"),
    ("wagon", "Универсал", "Универсал", "Wagon"),
    ("minivan", "Минивэн", "Минивэн", "Minivan"),
    ("pickup", "Пикап", "Пикап", "Pickup"),
    ("coupe", "Купе", "Купе", "Coupe"),
    ("convertible", "Открытый", "Открытый", "Convertible"),
)

CANONICAL_BODY_TYPE_SLUGS = frozenset(slug for slug, *_ in CANONICAL_BODY_TYPES)

# Engine volume / power labels accidentally imported as body types.
_JUNK_BODY_TYPE_NAME = re.compile(
    r"^\s*\d+([.,]\d+)?\s*(л\.?\s*с\.?|л\.?|hp|kw)\b",
    re.IGNORECASE,
)

_BODY_TYPE_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"седан", re.I), "sedan"),
    (re.compile(r"лифтбек|liftback", re.I), "liftback"),
    (re.compile(r"хэтчбек.*5|hatchback.*5", re.I), "hatchback-5d"),
    (re.compile(r"хэтчбек.*3|hatchback.*3", re.I), "hatchback-3d"),
    (re.compile(r"хэтчбек|hatchback", re.I), "hatchback-5d"),
    (re.compile(r"(джип|suv|внедорожник|кроссовер).*(^|\D)3(\D|$)|3\s*дв", re.I), "suv-3d"),
    (re.compile(r"джип|suv|внедорожник|кроссовер", re.I), "suv-5d"),
    (re.compile(r"универсал|wagon", re.I), "wagon"),
    (re.compile(r"минивэн|микроавтобус|minivan", re.I), "minivan"),
    (re.compile(r"пикап|pickup", re.I), "pickup"),
    (re.compile(r"купе|coupe", re.I), "coupe"),
    (re.compile(r"кабриолет|родстер|тарга|открыт|convertible|cabriolet|roadster", re.I), "convertible"),
    (re.compile(r"фургон|van\b", re.I), "minivan"),
    (re.compile(r"лимузин", re.I), "sedan"),
)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def is_valid_body_type_label(label: str | None) -> bool:
    if not label or not label.strip():
        return False
    if _JUNK_BODY_TYPE_NAME.search(label):
        return False
    if re.match(r"^\d", _normalize(label)):
        return False
    return resolve_body_type_slug(label) is not None


def resolve_body_type_slug(label: str) -> str | None:
    normalized = _normalize(label)
    for pattern, slug in _BODY_TYPE_RULES:
        if pattern.search(normalized):
            return slug
    return None


def canonical_body_type_names(slug: str) -> tuple[str, str, str] | None:
    for item_slug, mn, ru, en in CANONICAL_BODY_TYPES:
        if item_slug == slug:
            return mn, ru, en
    return None


def parse_body_type_filter_values(raw: str | list[str] | None) -> list[int]:
    """Parse body_type query param(s): comma-separated and/or repeated keys."""
    parts: list[str] = []
    if raw is None:
        return []
    if isinstance(raw, list):
        for item in raw:
            parts.extend(str(item).split(","))
    else:
        parts.extend(str(raw).split(","))
    ids: list[int] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            continue
    return ids


def filter_body_types_queryset(qs: QuerySet[BodyType]) -> QuerySet[BodyType]:
    junk = (
        Q(name_ru__regex=r"^\s*\d")
        | Q(name_en__regex=r"^\s*\d")
        | Q(name_mn__regex=r"^\s*\d")
    )
    filtered = qs.filter(slug__in=CANONICAL_BODY_TYPE_SLUGS).exclude(junk)
    order_cases = [
        When(slug=slug, then=index)
        for index, (slug, *_rest) in enumerate(CANONICAL_BODY_TYPES)
    ]
    return filtered.annotate(
        sort_order=Case(*order_cases, default=999, output_field=IntegerField())
    ).order_by("sort_order")


def ensure_canonical_body_types() -> None:
    for slug, mn, ru, en in CANONICAL_BODY_TYPES:
        BodyType.objects.update_or_create(
            slug=slug,
            defaults={"name_mn": mn, "name_ru": ru, "name_en": en},
        )
