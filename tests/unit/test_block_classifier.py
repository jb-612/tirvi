"""F11 T-03 + F52 T-02 — block heuristic classifier.

Spec: N01/F11 DE-03, DE-04. AC: US-01/AC-01, US-02/AC-01.
Spec: N02/F52 DE-02. AC: F52-S01/AC-02, F52-S02/AC-01.
FT-anchors: FT-075, FT-076. BT-anchors: BT-051, BT-054.
"""

from __future__ import annotations

from tirvi.blocks.classifier import classify_block
from tirvi.blocks.cues import (
    DATUM_PREFIXES,
    INSTRUCTION_PREFIXES,
    LETTER_CHOICE_RE,
)
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


class TestCueLexicon:
    """F52 T-02 — cue constants are importable from tirvi.blocks.cues."""

    def test_instruction_prefixes_contains_horaot(self):
        assert "הוראות" in INSTRUCTION_PREFIXES

    def test_instruction_prefixes_contains_kra_beiyun(self):
        assert any("קרא" in p for p in INSTRUCTION_PREFIXES)

    def test_instruction_prefixes_contains_sim_lev(self):
        assert any("שים" in p for p in INSTRUCTION_PREFIXES)

    def test_datum_prefixes_contains_netunim(self):
        assert "נתונים" in DATUM_PREFIXES

    def test_letter_choice_re_matches_alef_dot(self):
        assert LETTER_CHOICE_RE.match("א.")

    def test_letter_choice_re_matches_bet_dot(self):
        assert LETTER_CHOICE_RE.match("ב.")

    def test_letter_choice_re_rejects_plain_word(self):
        assert not LETTER_CHOICE_RE.match("שלום")


def _nw(text: str) -> "OCRWord":
    """Normal-height word for negative-example tests."""
    return _w(text, 100, 100, 200, 130)


class TestCueNegativeExamples:
    """F52 T-02 — blocks that do NOT match a cue fall through to the right default."""

    def test_regular_text_not_classified_as_instruction(self):
        # "זוהי פסקה" starts with neither הוראות / קרא בעיון / שים לב
        words = [_nw("זוהי"), _nw("פסקה"), _nw("רגילה"), _nw("מאוד"), _nw("ארוכה")]
        kind, _ = classify_block(words, _STATS)
        assert kind != "instruction"

    def test_non_numeric_prefix_not_question_stem(self):
        # "שאלה" alone (no digit) does not trigger question_stem cue
        words = [_nw("שאלה"), _nw("מעניינת"), _nw("מאוד"), _nw("כן")]
        kind, _ = classify_block(words, _STATS)
        assert kind != "question_stem"

    def test_two_letter_choices_not_multi_choice(self):
        # Only א. and ב. — below the ≥3 threshold
        words = [_nw("א."), _nw("ראשון"), _nw("ב."), _nw("שני"), _nw("טקסט"), _nw("נוסף")]
        kind, _ = classify_block(words, _STATS)
        assert kind != "multi_choice_options"

    def test_non_empty_normal_block_not_answer_blank(self):
        words = [_nw("מילה"), _nw("אחת"), _nw("שתיים"), _nw("שלוש")]
        kind, _ = classify_block(words, _STATS)
        assert kind != "answer_blank"
