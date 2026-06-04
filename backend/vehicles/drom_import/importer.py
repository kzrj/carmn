from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from django.db import transaction

from listings.models import Listing, ListingPhoto, ListingPriceHistory, ListingView, UserFavorite
from core.generation_photos import GenerationPhotoCatalog, generation_photo_url, index_generation_photos
from vehicles.drom_import.period import parse_period
from vehicles.drom_import.refs import ReferenceResolver, parse_body_type_label, parse_group_specs
from vehicles.drom_import.slugs import brand_slug, generation_slug, model_slug, trim_slug
from vehicles.generation_info import lookup_generation_info
from vehicles.models import Brand, Generation, Model, Trim


@dataclass
class ImportStats:
    brands_created: int = 0
    brands_updated: int = 0
    models_created: int = 0
    models_updated: int = 0
    generations_created: int = 0
    generations_updated: int = 0
    trims_created: int = 0
    trims_updated: int = 0
    files_processed: int = 0
    files_skipped: int = 0
    photos_saved: int = 0
    photos_failed: int = 0
    warnings: list[str] = field(default_factory=list)


def default_parsed_dir() -> Path:
    backend_dir = Path(__file__).resolve().parents[2]
    project_root = backend_dir.parent
    candidates = [
        Path("/data/drom/parsed"),
        project_root / "scripts" / "drom" / "parsed",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


def localized_names(label: str) -> dict[str, str]:
    value = label.strip()
    return {"name_mn": value, "name_ru": value, "name_en": value}


def clear_vehicle_catalog() -> None:
    ListingView.objects.all().delete()
    UserFavorite.objects.all().delete()
    ListingPriceHistory.objects.all().delete()
    ListingPhoto.objects.all().delete()
    Listing.objects.all().delete()
    Trim.objects.all().delete()
    Generation.objects.all().delete()
    Model.objects.all().delete()
    Brand.objects.all().delete()


def iter_parsed_files(parsed_dir: Path, brand: str | None = None) -> list[Path]:
    if brand:
        root = parsed_dir / brand
        if not root.is_dir():
            return []
        return sorted(root.glob("*.json"))
    return sorted(parsed_dir.glob("*/*.json"))


def generation_has_parsed_data(entry: dict) -> bool:
    return bool(entry.get("parsed")) and not entry.get("error")


def build_generation_name(entry: dict, model_data: dict | None = None) -> str:
    return lookup_generation_info(entry, model_data)


class DromImporter:
    def __init__(
        self,
        parsed_dir: Path,
        *,
        dry_run: bool = False,
        fetch_photos: bool = True,
        photo_delay: float = 0.3,
    ) -> None:
        self.parsed_dir = parsed_dir
        self.dry_run = dry_run
        self.fetch_photos = fetch_photos
        self.stats = ImportStats()
        self.refs = ReferenceResolver()
        self.photo_catalog = (
            GenerationPhotoCatalog(parsed_dir, delay_sec=photo_delay) if fetch_photos and not dry_run else None
        )

    def run(
        self,
        *,
        brand: str | None = None,
        replace: bool = False,
        on_file_done: Callable[[str, str, int], None] | None = None,
    ) -> ImportStats:
        files = iter_parsed_files(self.parsed_dir, brand=brand)
        if not files:
            self.stats.warnings.append(f"No parsed JSON files found in {self.parsed_dir}")
            return self.stats

        if self.dry_run:
            for path in files:
                self._import_file(path, commit=False)
            return self.stats

        if replace:
            with transaction.atomic():
                clear_vehicle_catalog()

        for path in files:
            with transaction.atomic():
                result = self._import_file(path, commit=True)
                if on_file_done and result:
                    brand_key, model_key, gen_count = result
                    on_file_done(brand_key, model_key, gen_count)
        return self.stats

    def _track(self, created: bool, entity: str) -> None:
        if entity == "brand":
            if created:
                self.stats.brands_created += 1
            else:
                self.stats.brands_updated += 1
        elif entity == "model":
            if created:
                self.stats.models_created += 1
            else:
                self.stats.models_updated += 1
        elif entity == "generation":
            if created:
                self.stats.generations_created += 1
            else:
                self.stats.generations_updated += 1
        elif entity == "trim":
            if created:
                self.stats.trims_created += 1
            else:
                self.stats.trims_updated += 1

    def _import_file(self, path: Path, *, commit: bool) -> tuple[str, str, int] | None:
        data = json.loads(path.read_text(encoding="utf-8"))
        generations = [item for item in data.get("generations") or [] if generation_has_parsed_data(item)]
        if not generations:
            self.stats.files_skipped += 1
            brand_name = data.get("brand_slug") or path.parent.name
            model_name = data.get("model_slug") or path.stem
            self.stats.warnings.append(f"{brand_name}/{model_name}: skipped (no parsed generations)")
            return None

        brand_key = data.get("brand_slug") or path.parent.name
        model_key = data.get("model_slug") or path.stem
        brand_label = data.get("brand_name") or brand_key
        model_label = data.get("model_name") or model_key

        if commit:
            brand_obj, created = Brand.objects.update_or_create(
                slug=brand_slug(brand_key),
                defaults={**localized_names(brand_label), "country": None},
            )
            self._track(created, "brand")

            model_obj, created = Model.objects.update_or_create(
                slug=model_slug(brand_key, model_key),
                defaults={**localized_names(model_label), "brand": brand_obj},
            )
            self._track(created, "model")
        else:
            brand_obj = None
            model_obj = None

        self.stats.files_processed += 1
        photos_index = index_generation_photos(data)

        for entry in generations:
            self._import_generation(
                brand_key=brand_key,
                model_key=model_key,
                model_obj=model_obj,
                model_data=data,
                entry=entry,
                photos_index=photos_index,
                commit=commit,
            )

        return brand_key, model_key, len(generations)

    def _import_generation(
        self,
        *,
        brand_key: str,
        model_key: str,
        model_obj: Model | None,
        model_data: dict | None,
        entry: dict,
        photos_index: dict[str, str],
        commit: bool,
    ) -> None:
        gen_key = entry.get("slug") or entry.get("id") or "generation"
        gen_slug_value = generation_slug(brand_key, model_key, str(gen_key))
        period = entry.get("period") or (entry.get("parsed") or {}).get("period")
        year_from, year_to = parse_period(period)
        body_label = parse_body_type_label(entry.get("frame_types"))
        body_type = self.refs.body_type(body_label) if commit else None
        generation_info = lookup_generation_info(entry, model_data)
        photo_url = generation_photo_url(entry, photos_index)

        if commit:
            generation_obj, created = Generation.objects.update_or_create(
                slug=gen_slug_value,
                defaults={
                    **localized_names(generation_info),
                    "generation_info": generation_info,
                    "model": model_obj,
                    "year_from": year_from,
                    "year_to": year_to,
                    "body_type": body_type,
                },
            )
            self._track(created, "generation")
            self._save_generation_photo(generation_obj, photo_url)
        else:
            generation_obj = None

        parsed = entry.get("parsed") or {}
        for group in parsed.get("groups") or []:
            specs = parse_group_specs(group.get("title"))
            group_body = body_type
            fuel = self.refs.fuel(specs["fuel"]) if commit else None
            transmission = self.refs.transmission(specs["transmission"]) if commit else None
            drive = self.refs.drive(specs["drive"]) if commit else None

            for period_block in group.get("periods") or []:
                for item in period_block.get("items") or []:
                    trim_id = item.get("id")
                    if trim_id is None:
                        continue
                    trim_name = (item.get("title") or "").strip() or str(trim_id)
                    trim_slug_value = trim_slug(brand_key, model_key, str(gen_key), trim_id)

                    if commit:
                        trim_obj, created = Trim.objects.update_or_create(
                            slug=trim_slug_value,
                            defaults={
                                **localized_names(trim_name),
                                "generation": generation_obj,
                                "body_type": group_body,
                                "fuel": fuel,
                                "transmission": transmission,
                                "drive": drive,
                            },
                        )
                        self._track(created, "trim")

    def _save_generation_photo(self, generation_obj: Generation, photo_url: str | None) -> None:
        if not photo_url or not self.photo_catalog:
            return
        image = self.photo_catalog.fetch_image(photo_url)
        if not image:
            self.stats.photos_failed += 1
            return
        filename = f"{generation_obj.slug}.jpg"
        generation_obj.photo.save(filename, image, save=True)
        self.stats.photos_saved += 1
