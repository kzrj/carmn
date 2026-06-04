from __future__ import annotations

import re

from django.db.models import Case, IntegerField, QuerySet, When

from references.models import DriveType, FuelType, TransmissionType

# Drom auto.drom.ru filter values (order preserved for UI).
CANONICAL_FUEL_TYPES: tuple[tuple[str, str, str, str], ...] = (
    ("petrol", "Бензин", "Бензин", "Petrol"),
    ("diesel", "Дизель", "Дизель", "Diesel"),
    ("electric", "Цахилгаан", "Электро", "Electric"),
    ("hybrid", "Гибрид", "Гибрид", "Hybrid"),
    ("lpg", "Газ", "ГБО", "LPG"),
)

CANONICAL_TRANSMISSIONS: tuple[tuple[str, str, str, str, str | None], ...] = (
    ("akpp", "АКПП", "АКПП", "Automatic", "automatic"),
    ("robot", "Робот", "Робот", "Robot", "automatic"),
    ("cvt", "Вариатор", "Вариатор", "CVT", "automatic"),
    ("manual", "Механик", "Механика", "Manual", None),
)

CANONICAL_DRIVE_TYPES: tuple[tuple[str, str, str, str], ...] = (
    ("awd", "4WD", "4WD", "4WD"),
    ("fwd", "Урд", "Передний", "FWD"),
    ("rwd", "Ард", "Задний", "RWD"),
)

CANONICAL_FUEL_SLUGS = frozenset(slug for slug, *_ in CANONICAL_FUEL_TYPES)
CANONICAL_TRANSMISSION_SLUGS = frozenset(slug for slug, *_ in CANONICAL_TRANSMISSIONS)
CANONICAL_DRIVE_SLUGS = frozenset(slug for slug, *_ in CANONICAL_DRIVE_TYPES)

_FUEL_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"бензин|petrol|gasoline", re.I), "petrol"),
    (re.compile(r"дизел|diesel", re.I), "diesel"),
    (re.compile(r"элект|electric|ev\b", re.I), "electric"),
    (re.compile(r"гибрид|hybrid|phev", re.I), "hybrid"),
    (re.compile(r"гбо|lpg|газ|метан|пропан|cng", re.I), "lpg"),
)

_TRANSMISSION_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"вариатор|cvt", re.I), "cvt"),
    (re.compile(r"робот|amt|dct|dsg", re.I), "robot"),
    (re.compile(r"механ|мкпп|manual|mt\b", re.I), "manual"),
    (re.compile(r"акпп|автомат|automatic|at\b", re.I), "akpp"),
)

_DRIVE_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"4wd|4x4|полн|awd|all.?wheel", re.I), "awd"),
    (re.compile(r"перед|fwd|front", re.I), "fwd"),
    (re.compile(r"зад|rear|rwd", re.I), "rwd"),
)

# Legacy import slugs remapped to canonical rows during cleanup.
LEGACY_TRANSMISSION_SLUG_MAP: dict[str, str] = {
    "automatic": "akpp",
    "auto": "akpp",
    "at": "akpp",
    "amt": "robot",
    "dct": "robot",
    "variator": "cvt",
    "mkpp": "manual",
    "mt": "manual",
}

LEGACY_FUEL_SLUG_MAP: dict[str, str] = {
    "gasoline": "petrol",
    "benzine": "petrol",
    "ev": "electric",
    "gas": "lpg",
    "cng": "lpg",
    "gbo": "lpg",
}

LEGACY_DRIVE_SLUG_MAP: dict[str, str] = {
    "4wd": "awd",
    "4x4": "awd",
    "full": "awd",
    "all-wheel": "awd",
    "front": "fwd",
    "rear": "rwd",
}


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def resolve_fuel_slug(label: str) -> str | None:
    normalized = _normalize(label)
    for pattern, slug in _FUEL_RULES:
        if pattern.search(normalized):
            return slug
    return None


def resolve_transmission_slug(label: str) -> str | None:
    normalized = _normalize(label)
    for pattern, slug in _TRANSMISSION_RULES:
        if pattern.search(normalized):
            return slug
    return None


def resolve_drive_slug(label: str) -> str | None:
    normalized = _normalize(label)
    for pattern, slug in _DRIVE_RULES:
        if pattern.search(normalized):
            return slug
    return None


def canonical_fuel_names(slug: str) -> tuple[str, str, str] | None:
    for item_slug, mn, ru, en in CANONICAL_FUEL_TYPES:
        if item_slug == slug:
            return mn, ru, en
    return None


def canonical_transmission_names(slug: str) -> tuple[str, str, str] | None:
    for item_slug, mn, ru, en, _group in CANONICAL_TRANSMISSIONS:
        if item_slug == slug:
            return mn, ru, en
    return None


def canonical_drive_names(slug: str) -> tuple[str, str, str] | None:
    for item_slug, mn, ru, en in CANONICAL_DRIVE_TYPES:
        if item_slug == slug:
            return mn, ru, en
    return None


def transmission_group(slug: str) -> str | None:
    for item_slug, *_rest, group in CANONICAL_TRANSMISSIONS:
        if item_slug == slug:
            return group
    return None


def _filter_canonical_queryset(
    qs: QuerySet,
    canonical: tuple,
    canonical_slugs: frozenset[str],
) -> QuerySet:
    order_cases = [
        When(slug=slug, then=index)
        for index, row in enumerate(canonical)
        for slug in (row[0],)
    ]
    return qs.filter(slug__in=canonical_slugs).annotate(
        sort_order=Case(*order_cases, default=999, output_field=IntegerField())
    ).order_by("sort_order")


def filter_fuel_types_queryset(qs: QuerySet[FuelType]) -> QuerySet[FuelType]:
    return _filter_canonical_queryset(qs, CANONICAL_FUEL_TYPES, CANONICAL_FUEL_SLUGS)


def filter_transmissions_queryset(qs: QuerySet[TransmissionType]) -> QuerySet[TransmissionType]:
    return _filter_canonical_queryset(qs, CANONICAL_TRANSMISSIONS, CANONICAL_TRANSMISSION_SLUGS)


def filter_drive_types_queryset(qs: QuerySet[DriveType]) -> QuerySet[DriveType]:
    return _filter_canonical_queryset(qs, CANONICAL_DRIVE_TYPES, CANONICAL_DRIVE_SLUGS)


def ensure_canonical_fuel_types() -> None:
    for slug, mn, ru, en in CANONICAL_FUEL_TYPES:
        FuelType.objects.update_or_create(
            slug=slug,
            defaults={"name_mn": mn, "name_ru": ru, "name_en": en},
        )


def ensure_canonical_transmissions() -> None:
    for slug, mn, ru, en, _group in CANONICAL_TRANSMISSIONS:
        TransmissionType.objects.update_or_create(
            slug=slug,
            defaults={"name_mn": mn, "name_ru": ru, "name_en": en},
        )


def ensure_canonical_drive_types() -> None:
    for slug, mn, ru, en in CANONICAL_DRIVE_TYPES:
        DriveType.objects.update_or_create(
            slug=slug,
            defaults={"name_mn": mn, "name_ru": ru, "name_en": en},
        )


def ensure_canonical_vehicle_refs() -> None:
    ensure_canonical_fuel_types()
    ensure_canonical_transmissions()
    ensure_canonical_drive_types()
