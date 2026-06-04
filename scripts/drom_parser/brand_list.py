"""Parse saved drom.ru/catalog/ HTML and export brands to JSON."""
from __future__ import annotations

import json
import re
from html import unescape
from urllib.parse import urlparse

from drom_parser.html_utils import read_html
from drom_parser.paths import BRANDS_FILE, CATALOG_HTML, MARKS_DIR

CDN_MEDIA_BASE = "https://r-kn.drom.ru/js/bundles/media/"


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/").split("/")
    return path[1] if len(path) >= 2 and path[0] == "catalog" else ""


def icon_filename(src: str) -> str:
    src = unescape(src.strip())
    if not src:
        return ""
    return src.replace("\\", "/").split("/")[-1]


def icon_cdn_url(filename: str) -> str:
    return f"{CDN_MEDIA_BASE}{filename}" if filename else ""


def icon_local_path(files_dir_name: str, filename: str) -> str:
    if not filename:
        return ""
    local = CATALOG_HTML.parent / files_dir_name / filename
    if not local.is_file():
        return ""
    return f"{files_dir_name}/{filename}"


def extract_page_data(html: str) -> dict:
    for script in re.findall(
        r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
        html,
        re.S,
    ):
        try:
            data = json.loads(script)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "firms" in data:
            return data
    raise RuntimeError("Could not find catalog page JSON with firms data")


def extract_icons(html: str, *, files_dir_name: str) -> dict[str, dict[str, str]]:
    icons: dict[str, dict[str, str]] = {}
    pattern = re.compile(
        r'<div class="frg44i0">'
        r'(?:'
        r'<img[^>]*src="(?P<light>[^"]+)"[^>]*>'
        r'(?:<img[^>]*src="(?P<dark>[^"]+)"[^>]*>)?'
        r')'
        r'<div class="frg44i1[^"]*"[^>]*><span[^>]*>(?P<name>[^<]+)</span></div>'
        r'<a[^>]*href="(?P<url>https://www\.drom\.ru/catalog/[^"]+)"[^>]*'
        r'data-ga-stats-va-payload="\{&quot;firm_name&quot;:&quot;(?P<slug>[^&]+)&quot;\}"',
        re.S,
    )
    for match in pattern.finditer(html):
        slug = match.group("slug")
        light = icon_filename(match.group("light"))
        dark = icon_filename(match.group("dark") or match.group("light"))
        icons[slug] = {
            "light": light,
            "dark": dark,
            "light_url": icon_cdn_url(light),
            "dark_url": icon_cdn_url(dark),
            "light_local": icon_local_path(files_dir_name, light),
            "dark_local": icon_local_path(files_dir_name, dark),
        }
    return icons


def build_brand_record(
    firm: dict,
    *,
    is_top: bool,
    icons: dict[str, dict[str, str]],
) -> dict:
    slug = firm.get("stats", {}).get("payload", {}).get("firm_name") or slug_from_url(
        firm.get("url", "")
    )
    icon = icons.get(slug, {})
    return {
        "id": firm.get("id"),
        "slug": slug,
        "name": firm.get("name", ""),
        "url": firm.get("url", "").rstrip("/") + "/",
        "is_top": is_top,
        "bold": bool(firm.get("bold")),
        "icon_light": icon.get("light", ""),
        "icon_dark": icon.get("dark", ""),
        "icon_light_url": icon.get("light_url", ""),
        "icon_dark_url": icon.get("dark_url", ""),
        "icon_light_local": icon.get("light_local", ""),
        "icon_dark_local": icon.get("dark_local", ""),
    }


def parse_catalog_brands(*, html_path=CATALOG_HTML, output_path=BRANDS_FILE) -> dict:
    if not html_path.is_file():
        raise FileNotFoundError(f"Catalog HTML not found: {html_path}")

    html = read_html(html_path)
    page = extract_page_data(html)
    files_dir_name = f"{html_path.stem}_files"
    icons = extract_icons(html, files_dir_name=files_dir_name)

    firms = page["firms"]
    top_slugs = {
        f.get("stats", {}).get("payload", {}).get("firm_name") or slug_from_url(f.get("url", ""))
        for f in firms.get("topFirms", [])
    }
    all_firms = firms.get("allFirms", [])

    brands = []
    for firm in all_firms:
        slug = firm.get("stats", {}).get("payload", {}).get("firm_name") or slug_from_url(
            firm.get("url", "")
        )
        brands.append(build_brand_record(firm, is_top=slug in top_slugs, icons=icons))
    brands.sort(key=lambda item: item["name"].lower())

    result = {
        "source": "https://www.drom.ru/catalog/",
        "source_file": html_path.name,
        "assets_dir": files_dir_name,
        "count": len(brands),
        "top_count": len(top_slugs),
        "bold_count": sum(1 for b in brands if b["bold"]),
        "icons_matched": sum(1 for b in brands if b["icon_light_local"]),
        "brands": brands,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def run_catalog_brands() -> None:
    result = parse_catalog_brands()
    print(
        f"Saved {result['count']} brands "
        f"({result['bold_count']} bold, {result['icons_matched']} with local icons) "
        f"to {BRANDS_FILE}"
    )
