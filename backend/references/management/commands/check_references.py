from __future__ import annotations

import sys

from django.core.management.base import BaseCommand

from references.body_types import CANONICAL_BODY_TYPE_SLUGS
from references.models import BodyType, DriveType, FuelType, TransmissionType
from references.vehicle_refs import (
    CANONICAL_DRIVE_SLUGS,
    CANONICAL_FUEL_SLUGS,
    CANONICAL_TRANSMISSION_SLUGS,
)


class Command(BaseCommand):
    help = "Fail if reference tables contain non-canonical slugs (post-cleanup smoke check)."

    def handle(self, *args, **options):
        checks = (
            (BodyType, CANONICAL_BODY_TYPE_SLUGS, "body types"),
            (FuelType, CANONICAL_FUEL_SLUGS, "fuel types"),
            (TransmissionType, CANONICAL_TRANSMISSION_SLUGS, "transmissions"),
            (DriveType, CANONICAL_DRIVE_SLUGS, "drive types"),
        )
        ok = True
        for model, canonical, label in checks:
            bad = list(
                model.objects.exclude(slug__in=canonical)
                .values_list("slug", flat=True)
                .order_by("slug")
            )
            if bad:
                ok = False
                self.stderr.write(self.style.ERROR(f"{label}: non-canonical slugs: {bad}"))
            else:
                count = model.objects.filter(slug__in=canonical).count()
                self.stdout.write(f"{label}: OK ({count} canonical rows)")

        if not ok:
            self.stderr.write(self.style.ERROR("Run cleanup_vehicle_refs and cleanup_body_types."))
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS("All reference tables are canonical."))
