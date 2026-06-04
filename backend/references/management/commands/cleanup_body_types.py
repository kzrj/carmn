from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from listings.models import Listing
from references.body_types import CANONICAL_BODY_TYPE_SLUGS, ensure_canonical_body_types
from references.models import BodyType
from vehicles.drom_import.importer import default_parsed_dir, iter_parsed_files
from vehicles.drom_import.refs import ReferenceResolver, parse_body_type_label
from vehicles.drom_import.slugs import generation_slug
from vehicles.models import Generation, Trim


def backfill_generation_body_types(parsed_dir: Path) -> int:
    refs = ReferenceResolver()
    updated = 0
    for path in iter_parsed_files(parsed_dir):
        data = json.loads(path.read_text(encoding="utf-8"))
        brand_key = data.get("brand_slug") or path.parent.name
        model_key = data.get("model_slug") or path.stem
        for lineup in data.get("model_line") or []:
            for entry in lineup.get("generations") or []:
                gen_slug = generation_slug(brand_key, model_key, str(entry.get("slug") or entry.get("id")))
                body_type = refs.body_type(parse_body_type_label(entry.get("frame_types")))
                if not body_type:
                    continue
                count = Generation.objects.filter(slug=gen_slug).update(body_type=body_type)
                if count:
                    updated += count
                    Trim.objects.filter(generation__slug=gen_slug).update(body_type=body_type)
    return updated


def sync_listing_body_types() -> int:
    updated = 0
    qs = Listing.objects.select_related("body_type", "trim__body_type", "generation__body_type")
    for listing in qs.iterator(chunk_size=500):
        resolved = None
        if listing.trim and listing.trim.body_type_id:
            resolved = listing.trim.body_type
        elif listing.generation and listing.generation.body_type_id:
            resolved = listing.generation.body_type
        elif listing.body_type_id and listing.body_type.slug in CANONICAL_BODY_TYPE_SLUGS:
            resolved = listing.body_type
        elif listing.body_type_id:
            resolved = listing.body_type

        if resolved and listing.body_type_id != resolved.id:
            Listing.objects.filter(pk=listing.pk).update(body_type=resolved)
            updated += 1
    return updated


class Command(BaseCommand):
    help = "Ensure canonical body types, backfill from catalog, sync listings, remove junk."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--parsed-dir",
            type=Path,
            default=None,
            help="Parsed drom catalog JSON directory",
        )
        parser.add_argument("--skip-catalog", action="store_true", help="Skip generation backfill from JSON")

    def handle(self, *args, **options):
        ensure_canonical_body_types()
        self.stdout.write("Canonical body types upserted.")

        if not options["skip_catalog"]:
            parsed_dir = options["parsed_dir"] or default_parsed_dir()
            if parsed_dir.is_dir():
                gen_count = backfill_generation_body_types(parsed_dir)
                self.stdout.write(f"Generations backfilled from catalog: {gen_count}.")
            else:
                self.stdout.write(self.style.WARNING(f"Parsed dir not found: {parsed_dir}"))

        listing_count = sync_listing_body_types()
        self.stdout.write(f"Listings synced: {listing_count}.")

        junk = BodyType.objects.exclude(slug__in=CANONICAL_BODY_TYPE_SLUGS)
        junk_count = junk.count()
        if junk_count:
            junk_ids = list(junk.values_list("id", flat=True))
            Generation.objects.filter(body_type_id__in=junk_ids).update(body_type=None)
            Trim.objects.filter(body_type_id__in=junk_ids).update(body_type=None)
            Listing.objects.filter(body_type_id__in=junk_ids).update(body_type=None)
            junk.delete()
            self.stdout.write(self.style.SUCCESS(f"Removed {junk_count} junk body type(s)."))
            sync_listing_body_types()
        else:
            self.stdout.write("No junk body types found.")

        self.stdout.write(self.style.SUCCESS("Done."))
