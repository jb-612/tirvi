"""F21 — YAML homograph override loader with mtime-keyed LRU cache.

Spec: N02/F21 DE-02. AC: US-01/AC-01. FT: FT-158, FT-159, FT-162.
"""

from __future__ import annotations

import functools
from pathlib import Path

import yaml

from tirvi.homograph.value_objects import HomographEntry


@functools.lru_cache(maxsize=4)
def _load_cached(path: str, mtime_ns: int) -> dict[str, str]:
    """Cache key includes mtime so file edits invalidate the cached map."""
    raw = Path(path).read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"malformed homograph YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("homograph YAML must be a mapping at top level")
    entries_raw = data.get("entries", [])
    overrides: dict[str, str] = {}
    for item in entries_raw:
        entry = _to_entry(item)
        if entry.pos_filter is not None:
            continue
        overrides.setdefault(entry.surface_form, entry.vocalized_form)
    return overrides


def _to_entry(item: dict) -> HomographEntry:
    try:
        surface = item["surface_form"]
        vocalized = item["vocalized_form"]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"homograph entry missing required field: {item!r}") from exc
    return HomographEntry(
        surface_form=str(surface),
        vocalized_form=str(vocalized),
        pos_filter=item.get("pos_filter"),
    )


def load_overrides(path: str | Path) -> dict[str, str]:
    """Public loader. Reads mtime, delegates to cached load."""
    p = Path(path)
    return _load_cached(str(p), p.stat().st_mtime_ns)
