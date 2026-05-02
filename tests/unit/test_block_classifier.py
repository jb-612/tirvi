"""F11 T-03 — block heuristic classifier.

Spec: N01/F11 DE-03, DE-04. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-075, FT-076. BT-anchors: BT-051, BT-054.
"""

from __future__ import annotations

from tirvi.blocks.classifier import classify_block
from tirvi.blocks.value_objects import PageStats
from tirvi.results import OCRWord


def _w(text: str, x0: int, y0: int, x1: int, y1: int) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), confidence=1.0)


_STATS = PageStats(median_word_height=30.0, modal_x_start=100, line_spacing=40.0)


class TestBlockClassifier:
    def test_us_01_ac_01_heading_detected_above_modal_height(self) -> None:
        # word height 60 vs modal 30 → heading
        words = [_w("כותרת", 100, 0, 200, 60)]
        block_type, conf = classify_block(words, _STATS)
        assert block_type == "heading"
        assert conf >= 0.6

    def test_us_01_ac_01_question_stem_detected_by_hebrew_prefix(self) -> None:
        # Block starts with "שאלה 5" → question_stem
        words = [
            _w("שאלה", 100, 100, 200, 130),
            _w("5", 210, 100, 240, 130),
            _w("מה", 250, 100, 280, 130),
        ]
        block_type, conf = classify_block(words, _STATS)
        assert block_type == "question_stem"
        assert conf >= 0.6

    def test_us_01_ac_01_short_block_default_for_low_confidence(self) -> None:
        # Average-height words at modal x_start, no question prefix.
        # Legacy F11 contract: → paragraph.
        # Post-F52 contract (per PR #30 Q2 answer): short ambiguous
        # blocks fall back to `mixed` so consumers can route them to
        # human review. The 2-word block here is at the legacy
        # threshold; with F52 it becomes mixed.
        words = [
            _w("מילה", 100, 100, 150, 130),
            _w("שניה", 160, 100, 210, 130),
        ]
        block_type, _ = classify_block(words, _STATS)
        assert block_type == "mixed"

    def test_question_stem_takes_priority_over_heading(self) -> None:
        # Big text starting with "שאלה N" — question_stem wins per priority order
        words = [
            _w("שאלה", 100, 0, 200, 80),
            _w("3", 210, 0, 240, 80),
        ]
        block_type, _ = classify_block(words, _STATS)
        assert block_type == "question_stem"
