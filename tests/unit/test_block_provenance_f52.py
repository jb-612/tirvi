"""F52 T-03 + T-04 — transformations[] provenance propagation.

T-04: when the classifier returns a confident non-fallback kind, the
constructed Block carries a transformations[] entry referencing
ADR-041 row #20.

T-03: PlanBlock surfaces the same transformations[] field; F22's
aggregator copies it through.

Spec: N02/F52 DE-03, DE-04. AC: F52-S03/AC-01, F52-S04/AC-01.
"""
from __future__ import annotations

from tirvi.blocks.aggregation import _make_block
from tirvi.blocks.value_objects import PageStats
from tirvi.results import OCRWord


def _w(text: str, x0: int = 100, y0: int = 0, x1: int = 200, y1: int = 30) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), confidence=1.0)


_STATS = PageStats(median_word_height=30.0, modal_x_start=100, line_spacing=40.0)


class TestT04ClassifierProvenance:
    def test_instruction_block_emits_provenance_entry(self):
        words = [_w("הוראות"), _w("קרא"), _w("בעיון"), _w("את")]
        block = _make_block(words, [0, 1, 2, 3], _STATS, seq=1)
        assert block.block_type == "instruction"
        assert len(block.transformations) == 1
        entry = block.transformations[0]
        assert entry["kind"] == "block_kind_classification"
        assert entry["to"] == "instruction"
        assert entry["confidence"] == 0.85
        assert entry["adr_row"] == "ADR-041 #20"

    def test_question_stem_block_emits_provenance_entry(self):
        words = [_w("שאלה"), _w("3"), _w("מהי"), _w("התשובה")]
        block = _make_block(words, [0, 1, 2, 3], _STATS, seq=2)
        assert block.block_type == "question_stem"
        assert len(block.transformations) == 1
        assert block.transformations[0]["to"] == "question_stem"

    def test_paragraph_default_does_not_emit_provenance(self):
        # Paragraph at confidence 0.5 — below threshold; no provenance.
        words = [_w("מילים"), _w("רגילות"), _w("לפסקה"), _w("ארוכה"), _w("יותר")]
        block = _make_block(words, [0, 1, 2, 3, 4], _STATS, seq=3)
        assert block.block_type == "paragraph"
        assert block.transformations == ()

    def test_mixed_fallback_does_not_emit_provenance(self):
        # `mixed` is the fallback per Q2 — no provenance for fallbacks.
        words = [_w("מילה")]
        block = _make_block(words, [0], _STATS, seq=4)
        assert block.block_type == "mixed"
        assert block.transformations == ()


class TestT03PlanBlockField:
    def test_plan_block_default_transformations_is_empty_tuple(self):
        from tirvi.plan.value_objects import PlanBlock
        pb = PlanBlock(
            block_id="b1", block_type="paragraph",
            tokens=(),
        )
        assert pb.transformations == ()

    def test_plan_block_explicit_transformations(self):
        from tirvi.plan.value_objects import PlanBlock
        provenance = (
            {"kind": "block_kind_classification", "to": "instruction",
             "confidence": 0.85, "adr_row": "ADR-041 #20"},
        )
        pb = PlanBlock(
            block_id="b1", block_type="instruction",
            tokens=(), transformations=provenance,
        )
        assert pb.transformations == provenance
