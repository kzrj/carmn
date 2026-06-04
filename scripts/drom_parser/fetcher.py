"""HTTP fetching helpers for drom.ru catalog pages."""
from __future__ import annotations

import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from drom_parser.html_utils import read_html

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
DEFAULT_DELAY_SEC = 0.7


def fetch_url(url: str, *, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "ru-RU,ru;q=0.9"})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
    for encoding in ("utf-8", "windows-1251", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def fetch_url_safe(url: str, *, timeout: int = 30) -> tuple[str | None, str | None]:
    try:
        return fetch_url(url, timeout=timeout), None
    except HTTPError as exc:
        return None, f"HTTP {exc.code}: {url}"
    except URLError as exc:
        return None, f"Network error: {exc.reason}"
    except TimeoutError:
        return None, f"Timeout: {url}"


class RateLimitedFetcher:
    def __init__(
        self,
        *,
        delay_sec: float = DEFAULT_DELAY_SEC,
        max_delay_sec: float = 8.0,
        backoff_factor: float = 1.5,
    ) -> None:
        self.delay_sec = delay_sec
        self.base_delay_sec = delay_sec
        self.max_delay_sec = max_delay_sec
        self.backoff_factor = backoff_factor
        self._last_fetch_at = 0.0

    def _should_backoff(self, error: str) -> bool:
        lowered = error.lower()
        return (
            "timeout" in lowered
            or "network error" in lowered
            or error.startswith("HTTP 5")
            or error.startswith("HTTP 429")
        )

    def _on_fetch_result(self, error: str | None) -> None:
        if error and self._should_backoff(error):
            self.delay_sec = min(self.delay_sec * self.backoff_factor, self.max_delay_sec)
            return
        if self.delay_sec > self.base_delay_sec:
            self.delay_sec = max(self.base_delay_sec, self.delay_sec / self.backoff_factor)

    def fetch(self, url: str) -> tuple[str | None, str | None]:
        elapsed = time.monotonic() - self._last_fetch_at
        if elapsed < self.delay_sec:
            time.sleep(self.delay_sec - elapsed)
        html, error = fetch_url_safe(url)
        self._last_fetch_at = time.monotonic()
        self._on_fetch_result(error)
        return html, error


def load_html(source: str, *, fetcher: RateLimitedFetcher | None = None) -> tuple[str | None, str | None]:
    if source.startswith("http://") or source.startswith("https://"):
        if fetcher is None:
            return fetch_url_safe(source)
        return fetcher.fetch(source)

    from pathlib import Path

    path = Path(source)
    if path.is_file():
        return read_html(path), None
    return None, f"File not found: {source}"
