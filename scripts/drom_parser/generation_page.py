"""Parse drom.ru generation page (/catalog/{brand}/{model}/g_*/)."""
from __future__ import annotations

import re
from pathlib import Path

from drom_parser.html_utils import (
    clean_text,
    extract_page_json,
    generation_slug_from_url,
    normalize_url,
    read_html,
)


def parse_link_item(item: dict | None) -> dict | None:
    if not item:
        return None
    return {
        "title": clean_text(item.get("title") or ""),
        "url": normalize_url(item.get("url") or ""),
    }


def parse_complectation_item(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "title": clean_text(item.get("title") or ""),
        "url": normalize_url(item.get("url") or ""),
        "period": clean_text(item.get("period") or ""),
        "price": clean_text(item.get("price") or ""),
        "trim_level": clean_text(item.get("type") or "") or None,
        "photo_hint": item.get("photoHint"),
        "video_hint": item.get("videoHint"),
    }


def parse_complectation_groups(complectations: dict | None) -> list[dict]:
    groups: list[dict] = []
    for element in (complectations or {}).get("elements") or []:
        periods: list[dict] = []
        for period_block in element.get("periods") or []:
            periods.append(
                {
                    "period": clean_text(period_block.get("period") or ""),
                    "items": [
                        parse_complectation_item(item)
                        for item in period_block.get("complectations") or []
                    ],
                }
            )

        groups.append(
            {
                "title": clean_text(element.get("title") or ""),
                "engine": [parse_link_item(item) for item in element.get("engine") or []],
                "frame": [parse_link_item(item) for item in element.get("frame") or []],
                "used_price": clean_text(element.get("price") or "") or None,
                "periods": periods,
            }
        )
    return groups


def parse_page_heading(html: str) -> dict:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if not match:
        return {"heading": "", "period": ""}
    heading_html = match.group(1)
    text = clean_text(re.sub(r"<[^>]+>", " ", heading_html))
    period_match = re.search(r"\(([^)]+)\)", text)
    return {
        "heading": text,
        "period": clean_text(period_match.group(1)) if period_match else "",
    }


def parse_generation_page(
    html: str,
    *,
    source_file: str = "",
    page_url: str = "",
) -> dict:
    page = extract_page_json(html, any_key="complectations")
    complectations = page.get("complectations") or {}
    groups = parse_complectation_groups(complectations)
    heading = parse_page_heading(html)

    current_url = normalize_url(page_url or page.get("currentUrl") or "")
    breadcrumbs = page.get("breadcrumbs") or []
    if not current_url and breadcrumbs:
        for item in reversed(breadcrumbs):
            url = normalize_url(item.get("url") or "")
            if "/g_" in url:
                current_url = url
                break

    trim_count = sum(
        len(period["items"])
        for group in groups
        for period in group["periods"]
    )

    return {
        "source": current_url,
        "source_file": source_file,
        "slug": generation_slug_from_url(current_url),
        "title": clean_text(complectations.get("title") or heading["heading"]),
        "subtitle": clean_text(complectations.get("subtitle") or ""),
        "heading": heading["heading"],
        "period": heading["period"],
        "breadcrumbs": [
            {"name": clean_text(item.get("name") or ""), "url": normalize_url(item.get("url") or "")}
            for item in breadcrumbs
        ],
        "groups": groups,
        "group_count": len(groups),
        "trim_count": trim_count,
    }


def parse_generation_page_file(html_path: Path, *, page_url: str = "") -> dict:
    html = read_html(html_path)
    return parse_generation_page(html, source_file=html_path.name, page_url=page_url)
