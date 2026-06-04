from __future__ import annotations

import hashlib
import re
import unicodedata


def sanitize_slug(value: str, *, max_len: int = 120) -> str:
    text = (value or "").strip().replace("~", "-").replace(" ", "-")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9_-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    if not text:
        text = "item"
    if len(text) <= max_len:
        return text
    digest = hashlib.md5(value.encode("utf-8")).hexdigest()[:8]
    keep = max_len - len(digest) - 1
    return f"{text[:keep].rstrip('-')}-{digest}"


def brand_slug(value: str) -> str:
    return sanitize_slug(value)


def model_slug(brand: str, model: str) -> str:
    return sanitize_slug(f"{brand}-{model}")


def generation_slug(brand: str, model: str, generation: str) -> str:
    return sanitize_slug(f"{brand}-{model}-{generation}")


def trim_slug(brand: str, model: str, generation: str, trim_id: str | int) -> str:
    return sanitize_slug(f"{brand}-{model}-{generation}-{trim_id}")
