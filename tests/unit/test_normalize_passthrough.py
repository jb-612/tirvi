"""F14 T-01 — pure pass-through normalization (POC numbering).

Spec: N02/F14 DE-02. AC: US-01/AC-01.
"""

from __future__ import annotations

from tirvi.normalize.passthrough import normalize_text
from tirvi.results import OCRWord


def _w(text: str, x0: int = 0, y0: int = 0, x1: int = 50, y1: int = 30) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), conf=1.0)


class TestNormalizePassthrough:
    def test_us_01_ac_01_clean_text_unchanged(self) -> None:
        words = [_w("שלום"), _w("עולם")]
        result = normalize_text(words)
        assert result.text == "שלום עולם"

    def test_us_01_ac_01_preserves_nfd_nikud(self) -> None:
        # alef + qamatz in NFD form must survive (no NFC normalization)
        nfd = "אָ"
        words = [_w(nfd)]
        result = normalize_text(words)
        assert result.text == nfd

    def test_empty_input_returns_empty(self) -> None:
        result = normalize_text([])
        assert result.text == ""
        assert result.spans == ()
