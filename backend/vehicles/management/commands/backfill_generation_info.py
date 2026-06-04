from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from vehicles.drom_import.importer import default_parsed_dir, iter_parsed_files
from vehicles.drom_import.slugs import generation_slug
from vehicles.generation_info import lookup_generation_info
from vehicles.models import Generation


class Command(BaseCommand):
    help = "Backfill Generation.generation_info from parsed Drom JSON files."

    def add_arguments(self, parser):
        parser.add_argument("--brand", help="Limit to one brand slug, e.g. toyota")
        parser.add_argument(
            "--parsed-dir",
            help="Override parsed JSON directory (default: scripts/drom/parsed)",
        )

    def handle(self, *args, **options):
        parsed_dir = Path(options["parsed_dir"]) if options["parsed_dir"] else default_parsed_dir()
        brand = options.get("brand")
        updated = 0
        missing = 0

        for path in iter_parsed_files(parsed_dir, brand=brand):
            data = json.loads(path.read_text(encoding="utf-8"))
            brand_key = data.get("brand_slug") or path.parent.name
            model_key = data.get("model_slug") or path.stem

            for entry in data.get("generations") or []:
                if not entry.get("parsed") or entry.get("error"):
                    continue

                gen_key = entry.get("slug") or entry.get("id") or "generation"
                slug = generation_slug(brand_key, model_key, str(gen_key))
                generation_info = lookup_generation_info(entry, data)

                count = Generation.objects.filter(slug=slug).update(
                    generation_info=generation_info,
                    name_mn=generation_info,
                    name_ru=generation_info,
                    name_en=generation_info,
                )
                if count:
                    updated += count
                else:
                    missing += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated} generations from {parsed_dir}"
                + (f"; {missing} slugs not found in DB" if missing else "")
            )
        )
