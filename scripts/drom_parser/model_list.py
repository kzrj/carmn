"""Parse saved drom.ru brand model-list pages and export models to JSON."""
from __future__ import annotations

import json
from pathlib import Path

from drom_parser.html_utils import (
    brand_slug_from_url,
    build_files_index,
    extract_page_json,
    local_photo_path,
    normalize_url,
    read_html,
    slug_from_catalog_url,
)
from drom_parser.paths import BRAND_PAGE_GLOB, BRANDS_FILE, DATA_DIR, MODELS_DIR


def extract_brand_list_page_json(html: str) -> dict:
    return extract_page_json(html, any_key="models")


def parse_popular_models(
    tech_info_table: dict | None,
    *,
    files_dir: Path,
    files_index: dict[str, str],
) -> dict[str, dict]:
    if not tech_info_table:
        return {}

    head = tech_info_table.get("head") or []
    body = tech_info_table.get("body") or []

    image_cells: list[dict] = []
    info_cells: list[dict] = []
    for column in head:
        name = column.get("name")
        if name == "image":
            image_cells = column.get("cells") or []
        elif name == "info":
            info_cells = column.get("cells") or []

    count = max(len(image_cells), len(info_cells))
    if not count:
        return {}

    body_by_index: list[dict[str, object]] = [{} for _ in range(count)]
    for row in body:
        row_name = row.get("name") or ""
        heading = row.get("heading") or ""
        cells = row.get("cells") or []
        for index in range(min(count, len(cells))):
            cell = cells[index]
            if isinstance(cell, dict) and "link" in cell:
                body_by_index[index][row_name] = {
                    "heading": heading,
                    "value": cell.get("value", ""),
                    "url": cell.get("link", ""),
                }
            else:
                value = cell.get("value", "") if isinstance(cell, dict) else cell
                body_by_index[index][row_name] = {
                    "heading": heading,
                    "value": value,
                }

    popular: dict[str, dict] = {}
    for index in range(count):
        image_cell = image_cells[index] if index < len(image_cells) else {}
        info_cell = info_cells[index] if index < len(info_cells) else {}
        url = normalize_url(image_cell.get("url") or info_cell.get("url") or "")
        if not url:
            continue

        slug = slug_from_catalog_url(url)
        photo_url = image_cell.get("x1") or image_cell.get("x2") or ""
        photo_url_2x = image_cell.get("x2") or ""
        specs: dict[str, str] = {}
        listings = body_by_index[index].get("bullCount")
        for row_name, payload in body_by_index[index].items():
            if row_name == "bullCount" or not isinstance(payload, dict):
                continue
            heading = str(payload.get("heading") or "").strip()
            value = payload.get("value", "")
            if heading:
                specs[heading] = value
        extra_info: dict[str, object] = {
            "title": info_cell.get("title") or "",
            "subtitle": info_cell.get("subtitle"),
            "caption": info_cell.get("caption"),
            "photo_url": photo_url,
            "photo_url_2x": photo_url_2x,
            "photo_local": local_photo_path(files_dir, files_index, photo_url),
            "specs": specs,
        }
        if isinstance(listings, dict):
            extra_info["listings"] = {
                "text": listings.get("value", ""),
                "url": listings.get("url", ""),
            }

        popular[url] = {
            "slug": slug,
            "name": info_cell.get("title") or slug.replace("_", " ").title(),
            "url": url,
            "extra_info": extra_info,
        }

    return popular


def parse_brand_page(html_path: Path) -> dict:
    html = read_html(html_path)
    page = extract_brand_list_page_json(html)
    files_dir = html_path.parent / f"{html_path.stem}_files"
    files_index = build_files_index(files_dir)

    brand_url = normalize_url(page.get("catalogUrl") or page.get("currentUrl") or "")
    brand_slug = brand_slug_from_url(brand_url) or page.get("f_name_url") or ""
    popular_by_url = parse_popular_models(
        page.get("techInfoTable"),
        files_dir=files_dir,
        files_index=files_index,
    )

    models_by_url: dict[str, dict] = {}
    for item in page.get("models") or []:
        url = normalize_url(item.get("url") or "")
        if not url:
            continue
        slug = (
            item.get("stats", {})
            .get("payload", {})
            .get("model_name")
            or slug_from_catalog_url(url)
        )
        models_by_url[url] = {
            "slug": slug,
            "name": item.get("name") or slug.replace("_", " ").title(),
            "url": url,
            "is_popular": url in popular_by_url,
            "has_panorama": bool(item.get("hasPanorama")),
            "extra_info": None,
        }

    for url, popular in popular_by_url.items():
        if url in models_by_url:
            models_by_url[url]["is_popular"] = True
            models_by_url[url]["extra_info"] = popular["extra_info"]
            if popular["name"] and not models_by_url[url]["name"]:
                models_by_url[url]["name"] = popular["name"]
        else:
            models_by_url[url] = {
                "slug": popular["slug"],
                "name": popular["name"],
                "url": url,
                "is_popular": True,
                "has_panorama": False,
                "extra_info": popular["extra_info"],
            }

    models = sorted(models_by_url.values(), key=lambda item: item["name"].lower())
    popular_count = sum(1 for model in models if model["is_popular"])

    return {
        "source": brand_url,
        "source_file": html_path.name,
        "assets_dir": files_dir.name if files_dir.is_dir() else "",
        "brand_slug": brand_slug,
        "brand_url": brand_url,
        "title": page.get("title") or "",
        "popular_block_title": (page.get("techInfoTable") or {}).get("title") or "",
        "count": len(models),
        "popular_count": popular_count,
        "photos_local_matched": sum(
            1
            for model in models
            if model.get("extra_info")
            and model["extra_info"].get("photo_local")
        ),
        "models": models,
    }


def load_brand_names() -> dict[str, str]:
    if not BRANDS_FILE.is_file():
        return {}
    data = json.loads(BRANDS_FILE.read_text(encoding="utf-8"))
    return {brand["slug"]: brand["name"] for brand in data.get("brands", [])}


def parse_all_brand_pages(*, data_dir=DATA_DIR, output_dir=MODELS_DIR) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    brand_names = load_brand_names()
    html_paths = sorted(data_dir.glob(BRAND_PAGE_GLOB))
    if not html_paths:
        raise FileNotFoundError(f"No brand pages found in {data_dir}")

    summary = []
    for html_path in html_paths:
        result = parse_brand_page(html_path)
        slug = result["brand_slug"]
        result["brand_name"] = brand_names.get(slug) or slug.replace("_", " ").title()

        output_path = output_dir / f"{slug}.json"
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        summary.append(result)
        print(
            f"{result['brand_name']} ({slug}): "
            f"{result['count']} models, {result['popular_count']} popular "
            f"-> {output_path.name}"
        )

    index = {
        "source_dir": str(data_dir),
        "brand_count": len(summary),
        "brands": [
            {
                "slug": item["brand_slug"],
                "name": item["brand_name"],
                "count": item["count"],
                "popular_count": item["popular_count"],
                "file": f"models/{item['brand_slug']}.json",
            }
            for item in sorted(summary, key=lambda item: item["brand_name"].lower())
        ],
    }
    index_path = output_dir / "index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved index for {index['brand_count']} brands to {index_path}")
    return summary
