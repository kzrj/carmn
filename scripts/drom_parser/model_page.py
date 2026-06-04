"""Parse drom.ru model generations page (/catalog/{brand}/{model}/)."""
from __future__ import annotations

from pathlib import Path

from drom_parser.html_utils import (
    build_files_index,
    clean_text,
    extract_model_page_json,
    local_photo_path,
    normalize_url,
    read_html,
    generation_slug_from_url,
    resolve_catalog_url,
    split_title_lines,
)


def parse_tech_info_table(
    tech_info_table: dict | None,
    *,
    catalog_url: str,
    files_dir: Path | None = None,
    files_index: dict[str, str] | None = None,
) -> list[dict]:
    if not tech_info_table:
        return []

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
        return []

    specs_by_index: list[dict[str, object]] = [{} for _ in range(count)]
    listings_by_index: list[dict[str, str] | None] = [None for _ in range(count)]

    for row in body:
        row_name = row.get("name") or ""
        heading = clean_text(row.get("heading") or "")
        cells = row.get("cells") or []
        for index in range(min(count, len(cells))):
            cell = cells[index]
            if row_name == "bullCount" and isinstance(cell, dict):
                listings_by_index[index] = {
                    "text": clean_text(cell.get("value") or ""),
                    "url": normalize_url(cell.get("link") or ""),
                }
                continue
            if isinstance(cell, dict) and "link" in cell:
                specs_by_index[index][row_name] = {
                    "heading": heading,
                    "value": clean_text(cell.get("value") or ""),
                    "url": normalize_url(cell.get("link") or ""),
                }
            else:
                value = cell.get("value", "") if isinstance(cell, dict) else cell
                specs_by_index[index][row_name] = {
                    "heading": heading,
                    "value": clean_text(str(value)),
                }

    generations: list[dict] = []
    for index in range(count):
        image_cell = image_cells[index] if index < len(image_cells) else {}
        info_cell = info_cells[index] if index < len(info_cells) else {}
        url = normalize_url(image_cell.get("url") or info_cell.get("url") or "", base=catalog_url)

        photo_url = image_cell.get("x1") or image_cell.get("x2") or ""
        photo_url_2x = image_cell.get("x2") or ""
        photo_local = ""
        if files_dir and files_index is not None:
            photo_local = local_photo_path(files_dir, files_index, photo_url)

        specs: dict[str, str] = {}
        for row_name, payload in specs_by_index[index].items():
            if not isinstance(payload, dict):
                continue
            row_heading = str(payload.get("heading") or "").strip()
            if row_heading:
                specs[row_heading] = str(payload.get("value") or "")

        generations.append(
            {
                "url": url,
                "title": clean_text(info_cell.get("title") or ""),
                "subtitle": clean_text(info_cell.get("subtitle") or ""),
                "body_type": clean_text(info_cell.get("caption") or ""),
                "photo_url": photo_url,
                "photo_url_2x": photo_url_2x,
                "photo_local": photo_local,
                "release_period": specs.get("Период выпуска", ""),
                "specs": specs,
                "listings": listings_by_index[index],
            }
        )

    return generations


def parse_generations_in_order(
    generations_in_order: list[dict] | None,
    *,
    catalog_url: str,
    files_dir: Path | None = None,
    files_index: dict[str, str] | None = None,
) -> list[dict]:
    markets: dict[int, dict] = {}

    for group in generations_in_order or []:
        group_title = clean_text(group.get("title") or "")
        generation_info = clean_text(group.get("generationInfo") or "")

        for item in group.get("items") or []:
            outlet = item.get("outlet") or {}
            market_id = outlet.get("country")
            if market_id not in markets:
                outlet_name = clean_text(outlet.get("name") or "")
                markets[market_id] = {
                    "id": market_id,
                    "slug": outlet_name.lower().replace(" ", "_"),
                    "title": f"Модельный ряд для {outlet_name}" if outlet_name else "",
                    "title_short": outlet_name,
                    "generations": [],
                }

            photo_url = item.get("src") or ""
            photo_url_2x = item.get("src2x") or ""
            photo_local = ""
            if files_dir and files_index is not None:
                photo_local = local_photo_path(files_dir, files_index, photo_url)

            name = group_title.split(",")[0].strip() if group_title else ""
            period = clean_text(item.get("title") or "")

            markets[market_id]["generations"].append(
                {
                    "id": str(item.get("id") or ""),
                    "slug": generation_slug_from_url(item.get("url") or ""),
                    "url": normalize_url(item.get("url") or "", base=catalog_url),
                    "name": name,
                    "period": period,
                    "generation_info": generation_info,
                    "frames": clean_text(item.get("frames") or ""),
                    "frame_types": clean_text(item.get("frameTypes") or ""),
                    "is_production_continues": bool(item.get("isProductionContinues")),
                    "is_new_auto": bool(item.get("isNewAuto")),
                    "is_coming_soon": bool(item.get("isComingSoon")),
                    "is_right_wheel": item.get("isRightWheel"),
                    "photo_url": photo_url,
                    "photo_url_2x": photo_url_2x,
                    "photo_local": photo_local,
                }
            )

    return sorted(markets.values(), key=lambda market: market.get("id") or 0)


def parse_model_line(
    generations_by_outlets: list[dict] | None,
    *,
    catalog_url: str,
    files_dir: Path | None = None,
    files_index: dict[str, str] | None = None,
) -> list[dict]:
    markets: list[dict] = []
    for outlet in generations_by_outlets or []:
        items: list[dict] = []
        for generation in outlet.get("generations") or []:
            name, period = split_title_lines(generation.get("title") or "")
            photo_url = generation.get("src") or ""
            photo_url_2x = generation.get("src2x") or ""
            photo_local = ""
            if files_dir and files_index is not None:
                photo_local = local_photo_path(files_dir, files_index, photo_url)

            items.append(
                {
                    "id": str(generation.get("id") or ""),
                    "slug": clean_text(generation.get("url") or "").strip("/"),
                    "url": normalize_url(generation.get("url") or "", base=catalog_url),
                    "name": name,
                    "period": period,
                    "generation_info": clean_text(generation.get("generationInfo") or ""),
                    "frames": clean_text(generation.get("frames") or ""),
                    "frame_types": clean_text(generation.get("frameTypes") or ""),
                    "is_production_continues": bool(generation.get("isProductionContinues")),
                    "is_new_auto": bool(generation.get("isNewAuto")),
                    "is_coming_soon": bool(generation.get("isComingSoon")),
                    "photo_url": photo_url,
                    "photo_url_2x": photo_url_2x,
                    "photo_local": photo_local,
                }
            )

        markets.append(
            {
                "id": outlet.get("id"),
                "slug": outlet.get("slug") or "",
                "title": clean_text(outlet.get("title") or ""),
                "title_short": clean_text(outlet.get("titleShort") or ""),
                "generations": items,
            }
        )
    return markets


def parse_model_page(
    html: str,
    *,
    source_file: str = "",
    assets_dir: str = "",
    files_dir: Path | None = None,
    files_index: dict[str, str] | None = None,
) -> dict:
    page = extract_model_page_json(html)
    catalog_url = resolve_catalog_url(page)

    if files_dir is None and assets_dir:
        files_dir = Path(assets_dir)

    model_line = parse_model_line(
        page.get("generationsByOutlets"),
        catalog_url=catalog_url,
        files_dir=files_dir,
        files_index=files_index,
    )
    if not any(market.get("generations") for market in model_line):
        model_line = parse_generations_in_order(
            page.get("generationsInOrder"),
            catalog_url=catalog_url,
            files_dir=files_dir,
            files_index=files_index,
        )
    generations_table = parse_tech_info_table(
        page.get("techInfoTable"),
        catalog_url=catalog_url,
        files_dir=files_dir,
        files_index=files_index,
    )

    generation_count = sum(len(market["generations"]) for market in model_line)

    return {
        "source": catalog_url,
        "source_file": source_file,
        "assets_dir": assets_dir,
        "brand_slug": page.get("f_name_url") or "",
        "brand_name": page.get("f_name") or "",
        "model_slug": page.get("m_name_url") or "",
        "model_name": page.get("modelName") or page.get("m_name") or "",
        "model_url": catalog_url,
        "title": clean_text(page.get("title") or ""),
        "model_line_title": "Модельный ряд",
        "generations_table_title": clean_text((page.get("techInfoTable") or {}).get("title") or ""),
        "model_line": model_line,
        "generations_table": generations_table,
        "generation_count": generation_count,
    }


def parse_model_page_file(html_path: Path) -> dict:
    html = read_html(html_path)
    files_dir = html_path.parent / f"{html_path.stem}_files"
    files_index = build_files_index(files_dir)
    result = parse_model_page(
        html,
        source_file=html_path.name,
        assets_dir=files_dir.name if files_dir.is_dir() else "",
        files_dir=files_dir if files_dir.is_dir() else None,
        files_index=files_index,
    )
    return result
