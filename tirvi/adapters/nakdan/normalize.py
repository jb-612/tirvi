"""F19 T-05 — Hebrew nikud NFC→NFD normalization.

Spec: N02/F19 DE-05. AC: US-01/AC-01.

Downstream G2P (F20) requires nikud in NFD form so that combining marks
sit on their own codepoints in deterministic order. The two-step
``NFC → NFD`` pipeline normalizes any precomposed input first to settle
ordering, then decomposes for the G2P contract.
"""

from __future__ import annotations

import unicodedata


def to_nfd(text: str) -> str:
    """Normalize ``text`` through NFC then NFD."""
    return unicodedata.normalize("NFD", unicodedata.normalize("NFC", text))
