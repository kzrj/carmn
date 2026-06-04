from __future__ import annotations

import re

CURRENT_MARKERS = (
    "н.в",
    "н. v",
    "по наст",
    "наст. время",
    "настоящее время",
    "present",
)

PERIOD_RE = re.compile(
    r"(\d{1,2})\.(\d{4})\s*-\s*(?:(\d{1,2})\.(\d{4})|(.+))",
    re.IGNORECASE,
)


def parse_period(value: str | None) -> tuple[int | None, int | None]:
    text = (value or "").strip()
    if not text:
        return None, None

    match = PERIOD_RE.search(text)
    if not match:
        year_match = re.search(r"(20\d{2}|19\d{2})", text)
        if year_match:
            year = int(year_match.group(1))
            return year, year
        return None, None

    month_from = int(match.group(1))
    year_from = int(match.group(2))
    _ = month_from

    if match.group(3) and match.group(4):
        return year_from, int(match.group(4))

    tail = (match.group(5) or "").strip().lower()
    if any(marker in tail for marker in CURRENT_MARKERS):
        return year_from, None

    year_match = re.search(r"(20\d{2}|19\d{2})", tail)
    if year_match:
        return year_from, int(year_match.group(1))

    return year_from, None
