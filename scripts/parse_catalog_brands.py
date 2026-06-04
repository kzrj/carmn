"""Backward-compatible entry point. Prefer: python -m drom_parser brands"""
from drom_parser.cli import main

if __name__ == "__main__":
    import sys

    sys.argv = [sys.argv[0], "brands"]
    raise SystemExit(main())
