from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from vehicles.drom_import.importer import DromImporter, default_parsed_dir


class Command(BaseCommand):
    help = "Import parsed drom.ru catalog JSON into Brand/Model/Generation/Trim tables."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--parsed-dir",
            type=Path,
            default=None,
            help="Directory with parsed JSON (default: scripts/drom/parsed)",
        )
        parser.add_argument("--brand", default=None, help="Import only one brand slug")
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete existing listings and vehicle catalog before import",
        )
        parser.add_argument("--dry-run", action="store_true", help="Parse files without writing to DB")
        parser.add_argument(
            "--no-photos",
            action="store_true",
            help="Skip downloading generation photos from parsed JSON",
        )
        parser.add_argument(
            "--photo-delay",
            type=float,
            default=0.3,
            help="Delay between photo downloads in seconds",
        )

    def handle(self, *args, **options) -> None:
        parsed_dir = options["parsed_dir"] or default_parsed_dir()
        if not parsed_dir.is_dir():
            host_hint = Path("scripts/drom/parsed")
            raise CommandError(
                f"Parsed directory not found: {parsed_dir}\n"
                f"On host check: ls {host_hint} | head\n"
                "If empty/missing — copy parsed JSON there.\n"
                "If files exist — recreate backend container so volume is mounted:\n"
                "  docker compose up -d --force-recreate backend\n"
                "Then run:\n"
                "  docker compose exec backend python manage.py import_drom --replace"
            )

        importer = DromImporter(
            parsed_dir,
            dry_run=options["dry_run"],
            fetch_photos=not options["no_photos"],
            photo_delay=options["photo_delay"],
        )
        stats = importer.run(
            brand=options["brand"],
            replace=options["replace"],
            on_file_done=lambda brand_key, model_key, gen_count: self.stdout.write(
                f"{brand_key}/{model_key}: {gen_count} generations"
            ),
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Import finished: "
                f"brands +{stats.brands_created}/~{stats.brands_updated}, "
                f"models +{stats.models_created}/~{stats.models_updated}, "
                f"generations +{stats.generations_created}/~{stats.generations_updated}, "
                f"trims +{stats.trims_created}/~{stats.trims_updated}, "
                f"photos {stats.photos_saved} saved / {stats.photos_failed} failed, "
                f"files {stats.files_processed}, skipped {stats.files_skipped}"
            )
        )

        if stats.warnings:
            self.stdout.write(self.style.WARNING(f"Warnings ({len(stats.warnings)}):"))
            for warning in stats.warnings:
                self.stdout.write(f"  - {warning}")
