"""F26 T-02 — YAP lattice response parser.

Spec: N02/F26 DE-02. AC: US-01/AC-01. FT-anchors: FT-133.

Walks ``response["lattice_md"]`` and emits one token dict per word
position (collapsing multi-edge ambiguity to the first edge).
"""

from __future__ import annotations

from typing import Any


def parse_lattice(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Project a YAP lattice response into an ordered list of token dicts."""
    lattice = response.get("lattice_md") or {}
    ordered_keys = sorted(lattice.keys(), key=lambda k: int(k))
    return [_first_edge(lattice[key]) for key in ordered_keys if lattice[key]]


def _first_edge(edges: list[dict[str, Any]]) -> dict[str, Any]:
    edge = edges[0]
    return {
        "surface": edge.get("surface", ""),
        "lemma": edge.get("lemma", ""),
        "CPOSTag": edge.get("CPOSTag", ""),
        "FPOSTag": edge.get("FPOSTag", ""),
        "feats": _parse_feats(edge.get("feats", "")),
    }


def _parse_feats(raw: str) -> dict[str, str]:
    if not raw:
        return {}
    out: dict[str, str] = {}
    for pair in raw.split("|"):
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        out[key] = value
    return out
