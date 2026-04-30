"""F14 T-02 — bbox→span round-trip invariant (POC numbering).

Spec: N02/F14 DE-02. AC: US-01/AC-01. FT-anchors: FT-094, FT-097.
"""

from __future__ import annotations

from tirvi.normalize.passthrough import normalize_text
from tirvi.results import OCRWord


def _w(text: str, idx: int) -> OCRWord:
    # Layout the words horizontally so each has a unique bbox tied to its index.
    return OCRWord(text=text, bbox=(idx * 60, 0, idx * 60 + 50, 30), conf=1.0)


class TestBboxSpanMap:
    def test_us_01_ac_01_span_src_word_indices_non_empty(self) -> None:
        words = [_w("שלום", 0), _w("עולם", 1)]
        result = normalize_text(words)
        for span in result.spans:
            assert len(span.src_word_indices) >= 1

    def test_us_01_ac_01_union_of_src_indices_equals_input(self) -> None:
        # Every input word index appears in exactly one span (round-trip invariant)
        words = [_w(f"w{i}", i) for i in range(5)]
        result = normalize_text(words)
        seen: list[int] = []
        for span in result.spans:
            seen.extend(span.src_word_indices)
        assert sorted(seen) == list(range(len(words)))

    def test_span_char_range_aligns_with_normalized_text(self) -> None:
        words = [_w("alpha", 0), _w("beta", 1)]
        result = normalize_text(words)
        for span in result.spans:
            assert result.text[span.start_char:span.end_char] == span.text
