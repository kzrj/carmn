from __future__ import annotations

import re

GENERATION_INFO_RE = re.compile(
    r"(\d+\s*[-\w]*\s*поколение(?:\s*,\s*[^,()]+)?)",
    re.IGNORECASE,
)


def lookup_generation_info(entry: dict, model_data: dict | None = None) -> str:
    """Resolve Drom-style generation label, e.g. «2 поколение, рестайлинг»."""
    direct = (entry.get("generation_info") or entry.get("subtitle") or "").strip()
    if direct:
        return direct

    gen_id = str(entry.get("id") or "").strip()
    if gen_id and model_data:
        for market in model_data.get("model_line") or []:
            for item in market.get("generations") or []:
                if str(item.get("id") or "") != gen_id:
                    continue
                info = (item.get("generation_info") or "").strip()
                if info:
                    return info

    parsed = entry.get("parsed") or {}
    heading = (parsed.get("heading") or "").strip()
    if heading:
        match = GENERATION_INFO_RE.search(heading)
        if match:
            return match.group(1).strip()

    name = (entry.get("name") or entry.get("title") or "").strip()
    return name or entry.get("slug") or "Generation"
