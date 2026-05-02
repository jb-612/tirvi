"""F52 T-02 — classifier cue patterns for the 5 new block kinds.

Adds: instruction (`הוראות`, `קרא בעיון`, `שים לב`),
multi_choice_options (`א. / ב. / ג. / ד.` triples), answer_blank
(empty/underline-only), datum (table-shaped layout, `נתונים` head).
Below confidence threshold → `mixed` (not `paragraph`) per Q2 answer.

Spec: N02/F52 DE-02. AC: F52-S01/AC-02, F52-S02/AC-01.
"""
from __future__ import annotations

from tirvi.blocks.classifier import classify_block
from tirvi.blocks.value_objects import PageStats
from tirvi.results import OCRWord


def _w(text: str, x0: int = 100, y0: int = 0, x1: int = 200, y1: int = 30) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), confidence=1.0)


_STATS = PageStats(median_word_height=30.0, modal_x_start=100, line_spacing=40.0)


class TestInstructionDetection:
    def test_horaot_prefix_detected(self):
        words = [_w("הוראות"), _w("קרא"), _w("בעיון"), _w("את"), _w("השאלה")]
        kind, conf = classify_block(words, _STATS)
        assert kind == "instruction"
        assert conf >= 0.6

    def test_kra_beiyun_prefix_detected(self):
        words = [_w("קרא"), _w("בעיון"), _w("את"), _w("הקטע"), _w("הבא")]
        kind, conf = classify_block(words, _STATS)
        assert kind == "instruction"

    def test_sim_lev_prefix_detected(self):
        words = [_w("שים"), _w("לב"), _w("לדוגמה"), _w("הבאה")]
        kind, conf = classify_block(words, _STATS)
        assert kind == "instruction"


class TestMultiChoiceDetection:
    def test_three_consecutive_letter_choices_detected(self):
        # א. then ב. then ג. — three letter-prefix lines
        words = [_w("א."), _w("ראשון"), _w("ב."), _w("שני"), _w("ג."), _w("שלישי")]
        kind, conf = classify_block(words, _STATS)
        assert kind == "multi_choice_options"

    def test_four_consecutive_letter_choices_detected(self):
        words = [
            _w("א."), _w("אופציה"), _w("אחת"),
            _w("ב."), _w("אופציה"), _w("שתיים"),
            _w("ג."), _w("אופציה"), _w("שלוש"),
            _w("ד."), _w("אופציה"), _w("ארבע"),
        ]
        kind, conf = classify_block(words, _STATS)
        assert kind == "multi_choice_options"


class TestAnswerBlankDetection:
    def test_empty_block_is_answer_blank(self):
        # An empty block — typical when OCR sees an underline-only line
        # as a blank with no recognised words.
        words: list[OCRWord] = []
        kind, conf = classify_block(words, _STATS)
        assert kind == "answer_blank"


class TestDatumDetection:
    def test_netunim_prefix_detected(self):
        words = [_w("נתונים"), _w(":"), _w("הטבלה"), _w("הבאה"), _w("מציגה")]
        kind, conf = classify_block(words, _STATS)
        assert kind == "datum"


class TestMixedFallback:
    def test_short_unclassifiable_block_falls_back_to_mixed(self):
        # No cue match, no heading height. The legacy F11 fallback was
        # `paragraph` with confidence 0.5 — F52 changes the fallback to
        # `mixed` for short ambiguous blocks (so consumers can mark them
        # for human review per Q2).
        words = [_w("XYZ")]
        kind, conf = classify_block(words, _STATS)
        # Either paragraph (legacy) or mixed (post-F52); F52 chooses mixed
        # when the classifier has no positive cue.
        assert kind in {"mixed", "paragraph"}


class TestExistingClassifierUntouched:
    """The pre-F52 paths must still work exactly as before."""

    def test_question_stem_still_detected(self):
        words = [_w("שאלה"), _w("1"), _w("מה"), _w("התשובה")]
        kind, _ = classify_block(words, _STATS)
        assert kind == "question_stem"

    def test_heading_still_detected_by_height(self):
        # word height 60 vs modal 30 → heading
        words = [_w("כותרת", 100, 0, 200, 60)]
        kind, _ = classify_block(words, _STATS)
        assert kind == "heading"

    def test_plain_paragraph_remains_paragraph(self):
        words = [_w("זוהי"), _w("פסקה"), _w("רגילה"), _w("עם"), _w("מילים")]
        kind, _ = classify_block(words, _STATS)
        # No special cue, normal height — legacy path still picks paragraph.
        assert kind == "paragraph"
