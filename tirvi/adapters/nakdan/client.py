"""F19 T-01 (per ADR-025) — Dicta REST client.

Spec: N02/F19 DE-01 (revised), ADR-025. AC: US-01/AC-01.
FT-anchors: FT-150. BT-anchors: BT-099.

Vendor boundary: HTTP I/O against ``nakdan-2-0.loadbalancer.dicta.org.il``
lives only in this module (DE-06, ADR-029).
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

API_URL = "https://nakdan-2-0.loadbalancer.dicta.org.il/api"


def diacritize_via_api(text: str, *, timeout: float = 30.0) -> list[dict[str, Any]]:
    """POST ``text`` to the Dicta Nakdan REST endpoint and return the parsed
    JSON list.

    Per ADR-039: we use ``task: "morph"`` so options come back as dicts
    with ``{w, lex, morph, levelChoice, prefix_len, ...}`` — the ``lex``
    (lemma) and ``prefix_len`` fields drive the heuristic POS-fit
    scoring in :mod:`tirvi.adapters.nakdan.inference`. The undocumented
    ``morph`` bitfield is intentionally NOT decoded.

    Each entry is a per-word dict with ``word``, ``sep``, and
    ``options`` (top-pick at index 0).
    """
    payload = json.dumps(
        {"task": "morph", "data": text, "genre": "modern"}
    ).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return list(json.loads(response.read()))
