"""F15 DE-08 — Lint CLI for the acronym lexicon YAML."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


def _load(path: str) -> dict:
    raw = Path(path).read_text(encoding="utf-8")
    return yaml.safe_load(raw) or {}


def _validate_entry(item: dict, idx: int) -> str | None:
    if "form" not in item:
        return f"entry #{idx}: missing 'form'"
    if "expansion" not in item:
        return f"entry #{idx}: missing 'expansion'"
    return None


def _validate(data: dict) -> str | None:
    if "version" not in data:
        return "missing top-level 'version'"
    seen: set[str] = set()
    for idx, item in enumerate(data.get("entries", [])):
        err = _validate_entry(item, idx)
        if err is not None:
            return err
        form = item["form"]
        if form in seen:
            return f"duplicate form: {form!r}"
        seen.add(form)
    return None


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python -m tirvi.acronym.lint <path>", file=sys.stderr)
        return 2
    path = argv[0]
    try:
        data = _load(path)
    except (OSError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    err = _validate(data)
    if err is not None:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
