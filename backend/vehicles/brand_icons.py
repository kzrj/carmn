from __future__ import annotations

import json
from pathlib import Path

from core.generation_photos import GenerationPhotoCatalog

EMPTY_ICON_NAMES = {"empty.gif", "empty.png"}


def default_catalog_brands_path() -> Path:
    backend_dir = Path(__file__).resolve().parents[1]
    project_root = backend_dir.parent
    candidates = [
        Path("/data/drom/marks/catalog_brands.json"),
        Path("/scripts/drom/marks/catalog_brands.json"),
        project_root / "scripts" / "drom" / "marks" / "catalog_brands.json",
        (backend_dir / ".." / "scripts" / "drom" / "marks" / "catalog_brands.json").resolve(),
    ]
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            return resolved
    return candidates[0]


def catalog_brands_search_paths() -> list[Path]:
    backend_dir = Path(__file__).resolve().parents[1]
    project_root = backend_dir.parent
    raw = [
        Path("/data/drom/marks/catalog_brands.json"),
        Path("/scripts/drom/marks/catalog_brands.json"),
        project_root / "scripts" / "drom" / "marks" / "catalog_brands.json",
        (backend_dir / ".." / "scripts" / "drom" / "marks" / "catalog_brands.json").resolve(),
    ]
    seen: set[Path] = set()
    paths: list[Path] = []
    for candidate in raw:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        paths.append(resolved)
    return paths


def load_catalog_brands(path: Path | None = None) -> dict[str, dict]:
    catalog_path = path or default_catalog_brands_path()
    if not catalog_path.is_file():
        return {}
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return {item["slug"]: item for item in data.get("brands") or []}


def resolve_icon_url(entry: dict) -> str | None:
    url = (entry.get("icon_light_url") or "").strip()
    filename = (entry.get("icon_light") or "").strip()
    if not url or filename in EMPTY_ICON_NAMES:
        return None
    return url


def fetch_brand_icon(url: str, *, delay_sec: float = 0.3):
    catalog = GenerationPhotoCatalog(delay_sec=delay_sec)
    return catalog.fetch_image(url)
