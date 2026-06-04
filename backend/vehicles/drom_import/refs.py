from __future__ import annotations

import re
from typing import TypeVar

from references.body_types import canonical_body_type_names, is_valid_body_type_label, resolve_body_type_slug
from references.models import BodyType, DriveType, FuelType, TransmissionType
from references.vehicle_refs import (
    canonical_drive_names,
    canonical_fuel_names,
    canonical_transmission_names,
    resolve_drive_slug,
    resolve_fuel_slug,
    resolve_transmission_slug,
)

RefModel = TypeVar("RefModel", BodyType, FuelType, TransmissionType, DriveType)

FUEL_ALIASES: dict[str, str] = {
    "бензин": "petrol",
    "бензиновый": "petrol",
    "дизель": "diesel",
    "дизельный": "diesel",
    "гибрид": "hybrid",
    "гибридный": "hybrid",
    "электро": "electric",
    "электрический": "electric",
    "электрич": "electric",
    "gas": "lpg",
    "газ": "lpg",
    "метан": "lpg",
    "пропан": "lpg",
    "водород": "electric",
}

TRANSMISSION_ALIASES: dict[str, str] = {
    "мкпп": "manual",
    "механическая": "manual",
    "механика": "manual",
    "акпп": "akpp",
    "автомат": "akpp",
    "автоматическая": "akpp",
    "робот": "robot",
    "роботизированная": "robot",
    "amt": "robot",
    "dct": "robot",
    "вариатор": "cvt",
    "cvt": "cvt",
}

DRIVE_ALIASES: dict[str, str] = {
    "передний": "fwd",
    "задний": "rwd",
    "полный": "awd",
    "4wd": "awd",
    "4x4": "awd",
    "awd": "awd",
}


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _match_alias(text: str, aliases: dict[str, str]) -> str | None:
    normalized = _normalize(text)
    for key, slug in aliases.items():
        if key in normalized:
            return slug
    return None


def split_frame_types(value: str | None) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[,;/]", value)
    return [part.strip() for part in parts if part.strip()]


def parse_body_type_label(value: str | None) -> str | None:
    for part in split_frame_types(value):
        if _normalize(part) in {"гибрид", "hybrid"}:
            continue
        return part
    return split_frame_types(value)[0] if split_frame_types(value) else None


def parse_group_specs(title: str | None) -> dict[str, str | None]:
    text = title or ""
    parts = [part.strip() for part in text.split(",") if part.strip()]
    fuel_label = transmission_label = drive_label = None

    for part in parts:
        lowered = _normalize(part)
        if fuel_label is None and _match_alias(lowered, FUEL_ALIASES):
            fuel_label = part.strip()
        if transmission_label is None and _match_alias(lowered, TRANSMISSION_ALIASES):
            transmission_label = part.strip()
        if drive_label is None and _match_alias(lowered, DRIVE_ALIASES):
            drive_label = part.strip()

    return {
        "fuel": fuel_label,
        "transmission": transmission_label,
        "drive": drive_label,
    }


class ReferenceResolver:
    def __init__(self) -> None:
        self._cache: dict[tuple[str, str], object] = {}

    def _get_or_create(self, model_cls: type[RefModel], slug: str, mn: str, ru: str, en: str) -> RefModel:
        cache_key = (model_cls.__name__, slug)
        if cache_key in self._cache:
            return self._cache[cache_key]

        obj, _ = model_cls.objects.update_or_create(
            slug=slug,
            defaults={
                "name_mn": mn,
                "name_ru": ru,
                "name_en": en,
            },
        )
        self._cache[cache_key] = obj
        return obj

    def body_type(self, label: str | None) -> BodyType | None:
        if not is_valid_body_type_label(label):
            return None
        slug = resolve_body_type_slug(label or "")
        if not slug:
            return None
        names = canonical_body_type_names(slug)
        if not names:
            return None
        mn, ru, en = names
        return self._get_or_create(BodyType, slug, mn, ru, en)

    def fuel(self, label: str | None) -> FuelType | None:
        if not label:
            return None
        slug = _match_alias(label, FUEL_ALIASES) or resolve_fuel_slug(label)
        if not slug:
            return None
        names = canonical_fuel_names(slug)
        if not names:
            return None
        mn, ru, en = names
        return self._get_or_create(FuelType, slug, mn, ru, en)

    def transmission(self, label: str | None) -> TransmissionType | None:
        if not label:
            return None
        slug = _match_alias(label, TRANSMISSION_ALIASES) or resolve_transmission_slug(label)
        if not slug:
            return None
        names = canonical_transmission_names(slug)
        if not names:
            return None
        mn, ru, en = names
        return self._get_or_create(TransmissionType, slug, mn, ru, en)

    def drive(self, label: str | None) -> DriveType | None:
        if not label:
            return None
        slug = _match_alias(label, DRIVE_ALIASES) or resolve_drive_slug(label)
        if not slug:
            return None
        names = canonical_drive_names(slug)
        if not names:
            return None
        mn, ru, en = names
        return self._get_or_create(DriveType, slug, mn, ru, en)
