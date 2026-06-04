"""Paths to drom.ru data files (HTML samples, JSON input/output)."""
from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = PACKAGE_DIR.parent
DATA_DIR = SCRIPTS_DIR / "drom"

MODELS_DIR = DATA_DIR / "models"
PARSED_DIR = DATA_DIR / "parsed"
SAMPLES_DIR = DATA_DIR / "models_by_models"
MARKS_DIR = DATA_DIR / "marks"
BRANDS_FILE = MARKS_DIR / "catalog_brands.json"

CATALOG_HTML = DATA_DIR / (
    "Каталог автомобилей - технические характеристики автомобилей, "
    "цены, комплектации.html"
)
BRAND_PAGE_GLOB = "Модельный ряд *.html"
