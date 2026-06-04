"""Orchestrate model and generation parsing for drom.ru catalog."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from drom_parser.fetcher import RateLimitedFetcher, load_html
from drom_parser.generation_page import parse_generation_page
from drom_parser.html_utils import clean_text
from drom_parser.model_page import parse_model_page
from drom_parser.paths import MODELS_DIR, PARSED_DIR

OUTPUT_DIR = PARSED_DIR


def load_popular_model_slugs(brand_slug: str) -> list[str]:
    return [
        model["slug"]
        for model in load_brand_models(brand_slug)
        if model.get("is_popular") and model.get("slug")
    ]


def load_brand_models(brand_slug: str) -> list[dict]:
    path = MODELS_DIR / f"{brand_slug}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Brand models file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("models") or []


def collect_generation_urls(model_page: dict) -> list[dict]:
    urls: dict[str, dict] = {}
    for market in model_page.get("model_line") or []:
        market_info = {
            "market_id": market.get("id"),
            "market_slug": market.get("slug"),
            "market_title": market.get("title"),
        }
        for generation in market.get("generations") or []:
            url = generation.get("url") or ""
            if not url or url in urls:
                continue
            urls[url] = {
                "url": url,
                "slug": generation.get("slug") or "",
                "id": generation.get("id") or "",
                "name": generation.get("name") or "",
                "period": generation.get("period") or "",
                "generation_info": clean_text(generation.get("generation_info") or ""),
                **market_info,
            }

    if urls:
        return list(urls.values())

    for row in model_page.get("generations_table") or []:
        url = row.get("url") or ""
        if not url or url in urls:
            continue
        subtitle = clean_text(row.get("subtitle") or "")
        urls[url] = {
            "url": url,
            "slug": url.rstrip("/").split("/")[-1],
            "id": "",
            "name": clean_text(row.get("title") or ""),
            "period": clean_text(row.get("release_period") or ""),
            "subtitle": subtitle,
            "generation_info": subtitle,
            "market_id": None,
            "market_slug": "",
            "market_title": "",
        }

    return list(urls.values())


def merge_generation_metadata(base: dict, parsed_generation: dict) -> dict:
    return {
        **base,
        "parsed": parsed_generation,
        "title": parsed_generation.get("title") or base.get("name"),
        "trim_count": parsed_generation.get("trim_count", 0),
        "group_count": parsed_generation.get("group_count", 0),
    }


def parse_model(
    model_url: str,
    *,
    fetcher: RateLimitedFetcher | None = None,
    fetch_generations: bool = True,
    generation_urls: list[str] | None = None,
) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    html, error = load_html(model_url, fetcher=fetcher)
    if error or not html:
        return None, [error or f"Empty response: {model_url}"]

    try:
        model_page = parse_model_page(html, source_file=model_url)
    except RuntimeError as exc:
        return None, [f"{model_url}: {exc}"]

    label = f"{model_page.get('brand_slug')}/{model_page.get('model_slug')}"
    generation_refs = collect_generation_urls(model_page)
    if generation_urls:
        allowed = set(generation_urls)
        generation_refs = [item for item in generation_refs if item["url"] in allowed]

    parsed_generations: list[dict] = []
    if fetch_generations:
        for ref in generation_refs:
            gen_html, gen_error = load_html(ref["url"], fetcher=fetcher)
            if gen_error or not gen_html:
                msg = gen_error or "empty response"
                errors.append(f"{label} -> поколение {ref.get('slug') or ref['url']}: {msg}")
                parsed_generations.append({**ref, "error": msg})
                continue
            try:
                generation_data = parse_generation_page(gen_html, source_file=ref["url"], page_url=ref["url"])
                parsed_generations.append(merge_generation_metadata(ref, generation_data))
            except RuntimeError as exc:
                errors.append(f"{label} -> поколение {ref.get('slug') or ref['url']}: {exc}")
                parsed_generations.append({**ref, "error": str(exc)})

    result = {
        **model_page,
        "generations": parsed_generations,
        "parsed_generation_count": sum(1 for item in parsed_generations if "parsed" in item),
        "failed_generation_count": sum(1 for item in parsed_generations if item.get("error")),
    }
    return result, errors


def parse_brand(
    brand_slug: str,
    *,
    model_slugs: list[str] | None = None,
    fetcher: RateLimitedFetcher | None = None,
    fetch_generations: bool = True,
    limit: int | None = None,
    skip_existing: bool = False,
    output_dir: Path | None = None,
    on_model_saved: Callable[[dict, Path], None] | None = None,
) -> tuple[list[dict], list[str], list[Path]]:
    models = load_brand_models(brand_slug)
    if model_slugs:
        allowed = set(model_slugs)
        models = [model for model in models if model.get("slug") in allowed]

    if limit is not None:
        models = models[:limit]

    results: list[dict] = []
    errors: list[str] = []
    saved_paths: list[Path] = []
    for model in models:
        model_slug = model.get("slug") or ""
        if skip_existing and model_slug and is_model_parsed(brand_slug, model_slug, output_dir=output_dir):
            continue

        url = model.get("url") or ""
        if not url:
            errors.append(f"Missing model URL for slug {model_slug}")
            continue
        parsed, model_errors = parse_model(
            url,
            fetcher=fetcher,
            fetch_generations=fetch_generations,
        )
        errors.extend(model_errors)
        if parsed:
            parsed["list_entry"] = {
                "slug": model_slug,
                "name": model.get("name"),
                "url": url,
                "is_popular": model.get("is_popular"),
            }
            results.append(parsed)
            path = save_model_result(parsed, output_dir=output_dir)
            saved_paths.append(path)
            if on_model_saved:
                on_model_saved(parsed, path)
    return results, errors, saved_paths


def model_output_path(brand_slug: str, model_slug: str, *, output_dir: Path | None = None) -> Path:
    output_root = output_dir or OUTPUT_DIR
    return output_root / brand_slug / f"{model_slug}.json"


def is_model_parsed(brand_slug: str, model_slug: str, *, output_dir: Path | None = None) -> bool:
    return model_output_path(brand_slug, model_slug, output_dir=output_dir).is_file()


def update_generation_counts(result: dict) -> None:
    generations = result.get("generations") or []
    result["parsed_generation_count"] = sum(1 for item in generations if "parsed" in item)
    result["failed_generation_count"] = sum(1 for item in generations if item.get("error"))


def find_models_with_failed_generations(*, output_dir: Path | None = None) -> list[tuple[str, str, Path]]:
    output_root = output_dir or OUTPUT_DIR
    matches: list[tuple[str, str, Path]] = []
    for path in sorted(output_root.glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("failed_generation_count"):
            matches.append((path.parent.name, path.stem, path))
    return matches


def retry_failed_generations_in_result(
    result: dict,
    *,
    fetcher: RateLimitedFetcher | None = None,
) -> tuple[dict, list[str]]:
    errors: list[str] = []
    label = f"{result.get('brand_slug')}/{result.get('model_slug')}"
    generations = result.get("generations") or []
    updated: list[dict] = []

    for item in generations:
        if not item.get("error"):
            updated.append(item)
            continue

        url = item.get("url") or ""
        if not url:
            errors.append(f"{label} -> поколение {item.get('slug') or '?'}: missing url")
            updated.append(item)
            continue

        gen_html, gen_error = load_html(url, fetcher=fetcher)
        if gen_error or not gen_html:
            msg = gen_error or "empty response"
            errors.append(f"{label} -> поколение {item.get('slug') or url}: {msg}")
            updated.append({**item, "error": msg})
            continue

        try:
            generation_data = parse_generation_page(gen_html, source_file=url, page_url=url)
            base = {key: value for key, value in item.items() if key not in {"error", "parsed", "title", "trim_count", "group_count"}}
            updated.append(merge_generation_metadata(base, generation_data))
        except RuntimeError as exc:
            errors.append(f"{label} -> поколение {item.get('slug') or url}: {exc}")
            updated.append({**item, "error": str(exc)})

    result = {**result, "generations": updated}
    update_generation_counts(result)
    return result, errors


def retry_failed_generations(
    *,
    brand_slug: str | None = None,
    model_slugs: list[str] | None = None,
    fetcher: RateLimitedFetcher | None = None,
    output_dir: Path | None = None,
    on_model_saved: Callable[[dict, Path], None] | None = None,
) -> tuple[list[dict], list[str], list[Path]]:
    targets = find_models_with_failed_generations(output_dir=output_dir)
    if brand_slug:
        targets = [item for item in targets if item[0] == brand_slug]
    if model_slugs:
        allowed = set(model_slugs)
        targets = [item for item in targets if item[1] in allowed]

    results: list[dict] = []
    errors: list[str] = []
    saved_paths: list[Path] = []
    for _, _, path in targets:
        result = json.loads(path.read_text(encoding="utf-8"))
        updated, model_errors = retry_failed_generations_in_result(result, fetcher=fetcher)
        errors.extend(model_errors)
        saved_path = save_model_result(updated, output_dir=output_dir)
        results.append(updated)
        saved_paths.append(saved_path)
        if on_model_saved:
            on_model_saved(updated, saved_path)
    return results, errors, saved_paths


def save_model_result(result: dict, *, output_dir: Path | None = None) -> Path:
    output_root = output_dir or OUTPUT_DIR
    brand_slug = result.get("brand_slug") or "unknown"
    model_slug = result.get("model_slug") or "unknown"
    target_dir = output_root / brand_slug
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"{model_slug}.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
