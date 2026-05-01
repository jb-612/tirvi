"""F15 — YAML lexicon loader with mtime-keyed LRU cache.

Spec: N02/F15 DE-02.
"""

from __future__ import annotations

import functools
from pathlib import Path

import yaml

from tirvi.acronym.value_objects import AcronymEntry, Lexicon


@functools.lru_cache(maxsize=4)
def _load_cached(path: str, mtime_ns: int) -> Lexicon:
    """Cache key includes mtime so file edits invalidate the cached Lexicon."""
    raw = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    version = str(data.get("version", ""))
    entries = tuple(_to_entry(item) for item in data.get("entries", []))
    return Lexicon(version=version, entries=entries)


def _to_entry(item: dict) -> AcronymEntry:
    return AcronymEntry(
        form=item["form"],
        expansion=item["expansion"],
        source=item.get("source", ""),
        context_tags=tuple(item.get("context_tags", ())),
    )


def from_yaml(path: str | Path) -> Lexicon:
    """Public loader. Resolves path, reads mtime, delegates to cached load."""
    p = Path(path)
    return _load_cached(str(p), p.stat().st_mtime_ns)


# Bind as classmethod-style helper on Lexicon so call-sites can use
# ``Lexicon.from_yaml(...)`` per the design hint.
Lexicon.from_yaml = staticmethod(from_yaml)  # type: ignore[attr-defined]
