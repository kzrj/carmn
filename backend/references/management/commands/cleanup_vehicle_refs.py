from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import models

from listings.models import Listing
from references.models import DriveType, FuelType, TransmissionType
from references.vehicle_refs import (
    CANONICAL_DRIVE_SLUGS,
    CANONICAL_FUEL_SLUGS,
    CANONICAL_TRANSMISSION_SLUGS,
    LEGACY_DRIVE_SLUG_MAP,
    LEGACY_FUEL_SLUG_MAP,
    LEGACY_TRANSMISSION_SLUG_MAP,
    ensure_canonical_vehicle_refs,
    resolve_drive_slug,
    resolve_fuel_slug,
    resolve_transmission_slug,
)
from vehicles.models import Trim


def _remap_fk(model_cls: type[models.Model], field: str, old_id: int, new_id: int) -> int:
    return model_cls.objects.filter(**{field: old_id}).update(**{field: new_id})


def _migrate_legacy_slugs(
    ref_model: type[FuelType | TransmissionType | DriveType],
    legacy_map: dict[str, str],
    fk_updates: list[tuple[type[models.Model], str]],
) -> int:
    migrated = 0
    for old_slug, new_slug in legacy_map.items():
        old = ref_model.objects.filter(slug=old_slug).first()
        new = ref_model.objects.filter(slug=new_slug).first()
        if not old or not new or old.id == new.id:
            continue
        for model_cls, field in fk_updates:
            _remap_fk(model_cls, field, old.id, new.id)
        old.delete()
        migrated += 1
    return migrated


def _resolve_or_none(ref_model, label: str | None, resolver):
    if not label:
        return None
    slug = resolver(label)
    if not slug:
        return None
    return ref_model.objects.filter(slug=slug).first()


def _cleanup_junk(
    ref_model: type[FuelType | TransmissionType | DriveType],
    canonical_slugs: frozenset[str],
    resolver,
    fk_updates: list[tuple[type[models.Model], str]],
) -> int:
    junk = ref_model.objects.exclude(slug__in=canonical_slugs)
    removed = 0
    for item in junk:
        replacement = _resolve_or_none(ref_model, item.name_ru, resolver) or _resolve_or_none(
            ref_model, item.name_en, resolver
        )
        if replacement and replacement.id != item.id:
            for model_cls, field in fk_updates:
                _remap_fk(model_cls, field, item.id, replacement.id)
        else:
            for model_cls, field in fk_updates:
                model_cls.objects.filter(**{field: item.id}).update(**{field: None})
        item.delete()
        removed += 1
    return removed


class Command(BaseCommand):
    help = "Ensure canonical fuel/transmission/drive refs, migrate legacy slugs, remove junk."

    def handle(self, *args, **options):
        ensure_canonical_vehicle_refs()
        self.stdout.write("Canonical fuel/transmission/drive upserted.")

        fuel_fks = [(Listing, "fuel_id"), (Trim, "fuel_id")]
        trans_fks = [(Listing, "transmission_id"), (Trim, "transmission_id")]
        drive_fks = [(Listing, "drive_id"), (Trim, "drive_id")]

        migrated = _migrate_legacy_slugs(FuelType, LEGACY_FUEL_SLUG_MAP, fuel_fks)
        migrated += _migrate_legacy_slugs(TransmissionType, LEGACY_TRANSMISSION_SLUG_MAP, trans_fks)
        migrated += _migrate_legacy_slugs(DriveType, LEGACY_DRIVE_SLUG_MAP, drive_fks)
        self.stdout.write(f"Legacy slug rows merged: {migrated}.")

        removed = _cleanup_junk(FuelType, CANONICAL_FUEL_SLUGS, resolve_fuel_slug, fuel_fks)
        removed += _cleanup_junk(TransmissionType, CANONICAL_TRANSMISSION_SLUGS, resolve_transmission_slug, trans_fks)
        removed += _cleanup_junk(DriveType, CANONICAL_DRIVE_SLUGS, resolve_drive_slug, drive_fks)
        self.stdout.write(self.style.SUCCESS(f"Removed {removed} junk reference row(s)."))
        self.stdout.write(self.style.SUCCESS("Done."))
