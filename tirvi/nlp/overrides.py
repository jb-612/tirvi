"""F18 T-03 — morphological homograph override table.

Spec: N02/F18 DE-03. AC: US-01/AC-02.

MORPH_HOMOGRAPH_OVERRIDES maps (surface_text, frozenset(morph_items)) to
the resolved NLPToken. F21 ships production entries; POC stub is empty.
"""

from __future__ import annotations

from tirvi.results import NLPToken

MORPH_HOMOGRAPH_OVERRIDES: dict[tuple[str, frozenset], NLPToken] = {}
