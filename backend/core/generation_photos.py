from __future__ import annotations

import hashlib
import json
import mimetypes
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


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


def model_json_path(parsed_dir: Path, brand_slug: str, model_slug: str) -> Path:
    file_slug = model_slug
    prefix = f"{brand_slug}-"
    if file_slug.startswith(prefix):
        file_slug = file_slug[len(prefix) :]
    return parsed_dir / brand_slug / f"{file_slug}.json"


def drom_generation_slug(model_slug: str, generation_slug_value: str) -> str:
    prefix = f"{model_slug}-"
    if generation_slug_value.startswith(prefix):
        return generation_slug_value[len(prefix) :]
    return generation_slug_value


def pick_photo_url(entry: dict) -> str | None:
    for key in ("photo_url", "photo_url_2x"):
        url = (entry.get(key) or "").strip()
        if url:
            return url
    return None


def prefer_larger_url(url: str | None, url_2x: str | None) -> str | None:
    if url_2x:
        return url_2x
    return url


def index_generation_photos(data: dict) -> dict[str, str]:
    photos: dict[str, str] = {}

    def put(slug: str | None, url: str | None) -> None:
        if slug and url and slug not in photos:
            photos[slug] = url

    for market in data.get("model_line") or []:
        for generation in market.get("generations") or []:
            put(
                generation.get("slug"),
                prefer_larger_url(generation.get("photo_url"), generation.get("photo_url_2x")),
            )

    for generation in data.get("generations") or []:
        put(
            generation.get("slug"),
            prefer_larger_url(generation.get("photo_url"), generation.get("photo_url_2x")),
        )

    for row in data.get("generations_table") or []:
        url = row.get("url") or ""
        slug = url.rstrip("/").split("/")[-1] if url else ""
        put(slug, prefer_larger_url(row.get("photo_url"), row.get("photo_url_2x")))

    return photos


def generation_photo_url(entry: dict, photos_index: dict[str, str] | None = None) -> str | None:
    url = pick_photo_url(entry)
    if url:
        return url
    slug = entry.get("slug")
    if slug and photos_index:
        return photos_index.get(str(slug))
    return None


class GenerationPhotoCatalog:
    def __init__(self, parsed_dir: Path | None = None, *, delay_sec: float = 0.3) -> None:
        self.parsed_dir = parsed_dir or default_parsed_dir()
        self.delay_sec = delay_sec
        self._model_photos: dict[tuple[str, str], dict[str, str]] = {}
        self._download_cache: dict[str, tuple[bytes, str]] = {}
        self._last_fetch_at = 0.0

    def lookup(self, *, brand_slug: str, model_slug: str, generation_slug_value: str) -> str | None:
        key = (brand_slug, model_slug)
        if key not in self._model_photos:
            self._model_photos[key] = self._load_model_photos(brand_slug, model_slug)
        drom_slug = drom_generation_slug(model_slug, generation_slug_value)
        return self._model_photos[key].get(drom_slug)

    def _load_model_photos(self, brand_slug: str, model_slug: str) -> dict[str, str]:
        path = model_json_path(self.parsed_dir, brand_slug, model_slug)
        if not path.is_file():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return index_generation_photos(data)

    def fetch_image(self, url: str) -> ContentFile | None:
        cache_key = hashlib.md5(url.encode("utf-8")).hexdigest()
        if cache_key in self._download_cache:
            raw, name = self._download_cache[cache_key]
            return ContentFile(raw, name=name)

        elapsed = time.monotonic() - self._last_fetch_at
        if elapsed < self.delay_sec:
            time.sleep(self.delay_sec - elapsed)

        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"})
        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read()
            self._last_fetch_at = time.monotonic()
        except (URLError, TimeoutError, OSError):
            return None

        extension = _guess_extension(url, raw)
        filename = f"{cache_key}{extension}"
        self._download_cache[cache_key] = (raw, filename)
        return ContentFile(raw, name=filename)


def _guess_extension(url: str, raw: bytes) -> str:
    path_ext = Path(url.split("?", 1)[0]).suffix.lower()
    if path_ext in {".jpg", ".jpeg", ".png", ".webp"}:
        return path_ext
    mime = mimetypes.guess_type(url)[0]
    if mime == "image/png":
        return ".png"
    if mime == "image/webp":
        return ".webp"
    if raw[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    return ".jpg"
