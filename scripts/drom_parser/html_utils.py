"""Shared helpers for reading drom.ru saved pages and embedded JSON."""
from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

BASE_URL = "https://www.drom.ru"


def read_html(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "windows-1251", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def normalize_url(url: str, *, base: str = BASE_URL) -> str:
    cleaned = unescape((url or "").strip())
    if not cleaned:
        return ""
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned.rstrip("/") + "/"
    return urljoin(base, cleaned).rstrip("/") + "/"


def brand_slug_from_url(url: str) -> str:
    path = urlparse(normalize_url(url)).path.strip("/").split("/")
    return path[1] if len(path) >= 2 and path[0] == "catalog" else ""


def slug_from_catalog_url(url: str) -> str:
    path = urlparse(normalize_url(url)).path.strip("/").split("/")
    if len(path) >= 2 and path[0] == "catalog":
        return path[2] if len(path) >= 3 else path[1]
    return ""


def generation_slug_from_url(url: str) -> str:
    path = urlparse(normalize_url(url)).path.strip("/").split("/")
    if not path:
        return ""
    last = path[-1]
    return last if last.startswith("g_") else ""


def photo_filename(url: str) -> str:
    if not url:
        return ""
    return unescape(url.strip()).replace("\\", "/").split("/")[-1].split("?")[0]


def build_files_index(files_dir: Path) -> dict[str, str]:
    if not files_dir.is_dir():
        return {}
    return {file_path.name.lower(): file_path.name for file_path in files_dir.iterdir() if file_path.is_file()}


def local_photo_path(files_dir: Path, files_index: dict[str, str], url: str) -> str:
    filename = photo_filename(url)
    if not filename:
        return ""
    resolved = files_index.get(filename.lower())
    if not resolved:
        return ""
    return f"{files_dir.name}/{resolved}"


def extract_json_blocks(html: str) -> list[dict]:
    blocks: list[dict] = []
    for script in re.findall(
        r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
        html,
        re.S,
    ):
        try:
            data = json.loads(script)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            blocks.append(data)
    return blocks


def extract_page_json(html: str, *, required_keys: set[str] | None = None, any_key: str | None = None) -> dict:
    blocks = extract_json_blocks(html)
    if not blocks:
        raise RuntimeError("Could not find page JSON")

    if required_keys:
        for data in blocks:
            if required_keys.issubset(data.keys()):
                return data

        merged: dict = {}
        for data in blocks:
            merged.update(data)
        if required_keys.issubset(merged.keys()):
            return merged

        keys = ", ".join(sorted(required_keys))
        raise RuntimeError(f"Could not find page JSON with keys: {keys}")

    if any_key:
        for data in blocks:
            if any_key in data:
                return data
        raise RuntimeError(f"Could not find page JSON with key: {any_key}")

    return blocks[-1]


def extract_model_page_json(html: str) -> dict:
    blocks = extract_json_blocks(html)
    if not blocks:
        raise RuntimeError("Could not find model page JSON")

    with_generations: dict | None = None
    with_table: dict | None = None

    for data in blocks:
        if "generationsByOutlets" in data and "techInfoTable" in data:
            return data
        if "generationsByOutlets" in data:
            with_generations = data
        if "techInfoTable" in data:
            with_table = data

    if with_generations and with_table:
        return {**with_table, **with_generations}

    if with_generations:
        return with_generations
    if with_table:
        if "generationsInOrder" in with_table:
            return with_table
        raise RuntimeError("Could not find model page JSON with generations and techInfoTable")


def split_title_lines(title: str) -> tuple[str, str]:
    parts = [part.strip() for part in (title or "").replace("\r\n", "\n").split("\n") if part.strip()]
    if len(parts) >= 2:
        return parts[0], parts[1]
    if len(parts) == 1:
        return parts[0], ""
    return "", ""


def resolve_catalog_url(page: dict) -> str:
    current_url = normalize_url(page.get("currentUrl") or "")
    path_parts = urlparse(current_url).path.strip("/").split("/")
    if len(path_parts) >= 3 and path_parts[0] == "catalog":
        return current_url

    brand_slug = page.get("f_name_url") or ""
    model_slug = page.get("m_name_url") or ""
    if brand_slug and model_slug:
        return normalize_url(f"/catalog/{brand_slug}/{model_slug}/")

    return normalize_url(page.get("catalogUrl") or current_url)


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", unescape(value or "")).strip()
