"""CLI for drom.ru catalog parser."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from drom_parser.brand_list import run_catalog_brands
from drom_parser.fetcher import RateLimitedFetcher
from drom_parser.generation_page import parse_generation_page_file
from drom_parser.model_list import parse_all_brand_pages
from drom_parser.model_page import parse_model_page_file
from drom_parser.paths import PARSED_DIR
from drom_parser.pipeline import (
    find_models_with_failed_generations,
    is_model_parsed,
    load_popular_model_slugs,
    parse_brand,
    parse_model,
    retry_failed_generations,
    save_model_result,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse drom.ru catalog pages.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    brands = subparsers.add_parser("brands", help="Parse catalog brands from saved HTML")
    brands.set_defaults(func=_cmd_brands)

    models = subparsers.add_parser("models", help="Parse brand model lists from saved HTML")
    models.set_defaults(func=_cmd_models)

    generations = subparsers.add_parser("generations", help="Parse model generations and trims")
    generations.add_argument("--brand", default=None, help="Brand slug, e.g. toyota")
    generations.add_argument("--model", action="append", dest="models", help="Model slug. Repeatable.")
    generations.add_argument("--popular", action="store_true", help="Parse popular models from brand JSON")
    generations.add_argument("--all-models", action="store_true", help="Parse all models from brand JSON")
    generations.add_argument("--limit", type=int, help="Limit number of models when using --all-models")
    generations.add_argument("--no-fetch-generations", action="store_true", help="Only parse model pages")
    generations.add_argument("--delay", type=float, default=2.0, help="Delay between HTTP requests (sec)")
    generations.add_argument("--skip-existing", action="store_true", help="Skip models with existing JSON output")
    generations.add_argument("--retry-failed", action="store_true", help="Retry only failed generations in existing JSON")
    generations.add_argument("--output-dir", type=Path, default=PARSED_DIR, help="Directory for JSON output")
    generations.add_argument("--local-model-page", type=Path, help="Parse a saved model HTML file")
    generations.add_argument("--local-generation-page", type=Path, help="Parse a saved generation HTML file")
    generations.add_argument("--generation-url", help="Original URL for a saved generation page")
    generations.set_defaults(func=_cmd_generations)

    return parser


def _cmd_brands(_: argparse.Namespace) -> int:
    run_catalog_brands()
    return 0


def _cmd_models(_: argparse.Namespace) -> int:
    parse_all_brand_pages()
    return 0


def _cmd_generations(args: argparse.Namespace) -> int:
    if args.local_generation_page:
        result = parse_generation_page_file(
            args.local_generation_page,
            page_url=args.generation_url or "",
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.local_model_page:
        result = parse_model_page_file(args.local_model_page)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    fetcher = RateLimitedFetcher(delay_sec=args.delay)

    def print_saved(result: dict, path: Path) -> None:
        print(
            f"{result.get('brand_slug')}/{result.get('model_slug')}: "
            f"{result.get('generation_count', 0)} generations, "
            f"{result.get('parsed_generation_count', 0)} with trims, "
            f"{result.get('failed_generation_count', 0)} failed "
            f"-> {path}"
        )

    if args.retry_failed:
        model_slugs = args.models
        if args.popular:
            if not args.brand:
                print("--popular with --retry-failed requires --brand.", file=sys.stderr)
                return 1
            if not model_slugs:
                model_slugs = load_popular_model_slugs(args.brand)
        results, errors, saved_paths = retry_failed_generations(
            brand_slug=args.brand,
            model_slugs=model_slugs,
            fetcher=fetcher,
            output_dir=args.output_dir,
            on_model_saved=print_saved,
        )
        if not saved_paths:
            pending = find_models_with_failed_generations(output_dir=args.output_dir)
            if pending:
                print("No matching models with failed generations.", file=sys.stderr)
            else:
                print("No failed generations found.", file=sys.stderr)
            return 0 if not pending else 1
        if errors:
            print(f"\nWarnings ({len(errors)}):", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        return 0

    brand = args.brand or "toyota"

    if args.popular:
        models = load_popular_model_slugs(brand)
        if not models:
            print(f"No popular models found for brand {brand!r}.", file=sys.stderr)
            return 1
    else:
        models = args.models
        if not models and not args.all_models:
            models = ["allion"]

    def print_saved(result: dict, path: Path) -> None:
        print(
            f"{result.get('brand_slug')}/{result.get('model_slug')}: "
            f"{result.get('generation_count', 0)} generations, "
            f"{result.get('parsed_generation_count', 0)} with trims "
            f"-> {path}"
        )

    if args.all_models:
        results, errors, saved_paths = parse_brand(
            brand,
            model_slugs=None,
            fetcher=fetcher,
            fetch_generations=not args.no_fetch_generations,
            limit=args.limit,
            skip_existing=args.skip_existing,
            output_dir=args.output_dir,
            on_model_saved=print_saved,
        )
    else:
        results = []
        errors = []
        saved_paths = []
        for model_slug in models or []:
            if args.skip_existing and is_model_parsed(brand, model_slug, output_dir=args.output_dir):
                print(f"{brand}/{model_slug}: skip (already parsed)")
                continue

            model_url = f"https://www.drom.ru/catalog/{brand}/{model_slug}/"
            result, model_errors = parse_model(
                model_url,
                fetcher=fetcher,
                fetch_generations=not args.no_fetch_generations,
            )
            errors.extend(model_errors)
            if result:
                result["list_entry"] = {
                    "slug": model_slug,
                    "name": result.get("model_name"),
                    "url": model_url,
                }
                results.append(result)
                path = save_model_result(result, output_dir=args.output_dir)
                saved_paths.append(path)
                print_saved(result, path)

    if not saved_paths:
        print("Nothing parsed.", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    if errors:
        print(f"\nWarnings ({len(errors)}):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)

    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
