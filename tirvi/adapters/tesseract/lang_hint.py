"""F08 T-04 — per-word ``lang_hint`` detector.

Spec: N01/F08 DE-04. AC: US-01/AC-01. FT-anchors: FT-058.

Per-word codepoint scan:

- ``"he"`` if any character is in the Hebrew block (U+05D0..U+05EA)
- ``"en"`` if all letter characters are ASCII A-Z / a-z
- ``None`` otherwise (mixed, digits-only, punctuation-only, empty)
"""

from __future__ import annotations

_HE_LO = 0x05D0
_HE_HI = 0x05EA


def detect_lang_hint(text: str) -> str | None:
    """Return ``"he"`` / ``"en"`` / ``None`` for a single OCR word."""
    if any(_HE_LO <= ord(c) <= _HE_HI for c in text):
        return "he"
    letters = [c for c in text if c.isalpha()]
    if letters and all(_is_ascii_letter(c) for c in letters):
        return "en"
    return None


def _is_ascii_letter(c: str) -> bool:
    o = ord(c)
    return (0x41 <= o <= 0x5A) or (0x61 <= o <= 0x7A)
