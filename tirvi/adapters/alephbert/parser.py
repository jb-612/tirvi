"""F26 T-02 — YAP CoNLL response parser.

Parses YAP's actual response format:
  md_lattice: CoNLL lattice string (disambiguated morphology)
  dep_tree:   CoNLL dependency string (one token per line)

Disambiguated lattice line format:
  from_node TAB to_node TAB surface TAB lemma TAB CPOS TAB FPOS TAB feats TAB token_id

Dependency tree line format:
  id TAB surface TAB lemma TAB CPOS TAB FPOS TAB feats TAB head TAB dep_rel TAB _ TAB _
"""

from __future__ import annotations

from typing import Any


def parse_yap_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse YAP's JSON response into a list of token dicts.

    Uses dep_tree if available (has head/dep_rel), else falls back to md_lattice.
    """
    dep_tree = response.get("dep_tree", "").strip()
    md_lattice = response.get("md_lattice", "").strip()

    if dep_tree:
        return _parse_dep_tree(dep_tree)
    if md_lattice:
        return _parse_md_lattice(md_lattice)
    return []


def _parse_dep_tree(text: str) -> list[dict[str, Any]]:
    """Parse CoNLL dep_tree: id surface lemma CPOS FPOS feats head dep_rel _ _"""
    tokens = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 8:
            continue
        feats = _parse_feats(parts[5]) if parts[5] not in ("_", "") else {}
        tokens.append({
            "surface": parts[1],
            "lemma": parts[2],
            "CPOSTag": parts[3],
            "FPOSTag": parts[4],
            "feats": feats,
            "dep_head": int(parts[6]),
            "dep_rel": parts[7],
        })
    return tokens


def _parse_md_lattice(text: str) -> list[dict[str, Any]]:
    """Parse CoNLL md_lattice: from to surface lemma CPOS FPOS feats token_id"""
    seen: set[int] = set()
    tokens: list[dict[str, Any]] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        token_id = int(parts[7]) if len(parts) > 7 else -1
        if token_id in seen:
            continue
        seen.add(token_id)
        feats = _parse_feats(parts[6]) if parts[6] not in ("_", "") else {}
        tokens.append({
            "surface": parts[2],
            "lemma": parts[3],
            "CPOSTag": parts[4],
            "FPOSTag": parts[5],
            "feats": feats,
        })
    return tokens


def _parse_feats(raw: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for pair in raw.split("|"):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        out[key] = value
    return out
