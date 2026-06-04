from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from vehicles.brand_icons import (
    catalog_brands_search_paths,
    default_catalog_brands_path,
    fetch_brand_icon,
    load_catalog_brands,
    resolve_icon_url,
)
from vehicles.models import Brand


class Command(BaseCommand):
    help = "Download missing brand icons from drom.ru catalog metadata."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--catalog",
            type=Path,
            default=None,
            help="Path to catalog_brands.json (default: scripts/drom/marks/catalog_brands.json)",
        )
        parser.add_argument("--brand", default=None, help="Fetch icon for one brand slug only")
        parser.add_argument("--force", action="store_true", help="Replace existing icons")
        parser.add_argument(
            "--delay",
            type=float,
            default=0.3,
            help="Delay between downloads in seconds",
        )

    def handle(self, *args, **options) -> None:
        catalog_path = options["catalog"] or default_catalog_brands_path()
        if not catalog_path.is_file():
            tried = "\n  ".join(str(path) for path in catalog_brands_search_paths())
            raise CommandError(
                f"Catalog brands file not found: {catalog_path}\n"
                f"Tried:\n  {tried}\n"
                "Recreate backend so scripts are mounted:\n"
                "  docker compose up -d --force-recreate backend"
            )

        catalog = load_catalog_brands(catalog_path)
        qs = Brand.objects.all().order_by("slug")
        if options["brand"]:
            qs = qs.filter(slug=options["brand"])

        saved = 0
        skipped = 0
        missing = 0
        failed = 0

        for brand in qs:
            if brand.icon and not options["force"]:
                skipped += 1
                continue

            entry = catalog.get(brand.slug)
            if not entry:
                missing += 1
                self.stdout.write(self.style.WARNING(f"{brand.slug}: not in catalog metadata"))
                continue

            icon_url = resolve_icon_url(entry)
            if not icon_url:
                missing += 1
                self.stdout.write(self.style.WARNING(f"{brand.slug}: no icon URL in catalog metadata"))
                continue

            image = fetch_brand_icon(icon_url, delay_sec=options["delay"])
            if not image:
                failed += 1
                self.stdout.write(self.style.ERROR(f"{brand.slug}: download failed ({icon_url})"))
                continue

            filename = f"{brand.slug}{Path(icon_url.split('?', 1)[0]).suffix or '.png'}"
            brand.icon.save(filename, image, save=True)
            saved += 1
            self.stdout.write(f"{brand.slug}: saved")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: saved {saved}, skipped {skipped}, missing {missing}, failed {failed}"
            )
        )
