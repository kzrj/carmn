"""Querysets for FK fields: only drom-aligned canonical reference rows."""

from __future__ import annotations

from django.db.models import QuerySet

from references.body_types import CANONICAL_BODY_TYPE_SLUGS
from references.models import BodyType, DriveType, FuelType, TransmissionType
from references.vehicle_refs import (
    CANONICAL_DRIVE_SLUGS,
    CANONICAL_FUEL_SLUGS,
    CANONICAL_TRANSMISSION_SLUGS,
)


def canonical_body_types() -> QuerySet[BodyType]:
    return BodyType.objects.filter(slug__in=CANONICAL_BODY_TYPE_SLUGS)


def canonical_fuel_types() -> QuerySet[FuelType]:
    return FuelType.objects.filter(slug__in=CANONICAL_FUEL_SLUGS)


def canonical_transmissions() -> QuerySet[TransmissionType]:
    return TransmissionType.objects.filter(slug__in=CANONICAL_TRANSMISSION_SLUGS)


def canonical_drive_types() -> QuerySet[DriveType]:
    return DriveType.objects.filter(slug__in=CANONICAL_DRIVE_SLUGS)
