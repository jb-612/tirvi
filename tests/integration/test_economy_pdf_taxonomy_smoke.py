# N02/F52 T-06 — Phase-0 demo verification: block-kind taxonomy on Economy.pdf.
#
# Spec: N02/F52 DE-05. AC: F52-S06/AC-01.
# Dependency: T-05, F22-T-* (existing).
#
# Runs the full pipeline (OCR words → block segmentation → F52 classifier →
# F22 ReadingPlan) on a synthetic representation of Economy.pdf page 1.
#
# Phase-0 success criterion (roadmap §E):
#   At least one question_stem block is identified whose text contains
#   a question marker (`?` or `שאלה`).
#
# Uses synthetic OCR words rather than live Tesseract to keep this test
# self-contained in CI. OCR word shapes are representative of the real
# Economy.pdf page 1 layout (words extracted from the PDF manually for
# fixture authoring).

from __future__ import annotations

import pytest

from tirvi.blocks.aggregation import build_blocks
from tirvi.blocks.value_objects import PageStats
from tirvi.normalize import NormalizedText, Span
from tirvi.plan.aggregates import ReadingPlan
from tirvi.results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
    OCRWord,
)

# ---------------------------------------------------------------------------
# Economy.pdf page 1 — synthetic OCR word representation.
# Words are laid out in reading order with representative bboxes.
# Vertical gaps between blocks are large enough to trigger segmentation.
# ---------------------------------------------------------------------------

def _w(text: str, x0: int, y0: int, x1: int, y1: int) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), confidence=0.9)


# Block 0: heading — "כלכלה" at large height
# Block 1: instruction — "הוראות: קרא את השאלות בעיון לפני שתענה"
# Block 2: question_stem — "שאלה 1 מהו המחיר שיווי המשקל?"
# Block 3: datum — "נתונים: עקומת הביקוש..."
# Block 4: question_stem — "שאלה 2 חשב את עודף הצרכן ?"
# Block 5: paragraph — regular text

_ECONOMY_WORDS: list[OCRWord] = [
    # Block 0: heading (y0..y1 = 0..60, height=60 >> modal 30 → heading)
    _w("כלכלה",         100,   0, 300,  60),
    # Block 1: instruction — starts with "הוראות" (gap after heading)
    _w("הוראות",        100, 120, 220, 150),
    _w(":",             225, 120, 235, 150),
    _w("קרא",           240, 120, 290, 150),
    _w("את",            295, 120, 320, 150),
    _w("השאלות",        325, 120, 420, 150),
    _w("בעיון",         425, 120, 490, 150),
    _w("לפני",          495, 120, 540, 150),
    _w("שתענה",         545, 120, 615, 150),
    # Block 2: question_stem — starts with "שאלה N" (gap after instruction)
    _w("שאלה",         100, 220, 200, 250),
    _w("1",            205, 220, 220, 250),
    _w("מהו",          225, 220, 275, 250),
    _w("המחיר",        280, 220, 355, 250),
    _w("שיווי",        360, 220, 420, 250),
    _w("המשקל",        425, 220, 510, 250),
    _w("?",            515, 220, 525, 250),
    # Block 3: datum — starts with "נתונים" (gap after question_stem)
    _w("נתונים",       100, 320, 220, 350),
    _w(":",            225, 320, 235, 350),
    _w("עקומת",        240, 320, 320, 350),
    _w("הביקוש",       325, 320, 420, 350),
    # Block 4: question_stem — starts with "שאלה N" (gap after datum)
    _w("שאלה",         100, 420, 200, 450),
    _w("2",            205, 420, 220, 450),
    _w("חשב",          225, 420, 275, 450),
    _w("את",           280, 420, 310, 450),
    _w("עודף",         315, 420, 375, 450),
    _w("הצרכן",        380, 420, 455, 450),
    _w("?",            460, 420, 470, 450),
    # Block 5: paragraph — plain prose (gap after question_stem)
    _w("מדיניות",      100, 520, 210, 550),
    _w("ממשלתית",      215, 520, 330, 550),
    _w("משפיעה",       335, 520, 430, 550),
    _w("על",           435, 520, 460, 550),
    _w("השוק",         465, 520, 530, 550),
]

_PAGE_STATS = PageStats(
    median_word_height=30.0,
    modal_x_start=100,
    line_spacing=40.0,
)


def _build_synthetic_inputs(blocks):
    """Build minimal ReadingPlan inputs from classifier-produced blocks."""
    all_words = _ECONOMY_WORDS
    spans = tuple(
        Span(
            text=all_words[idx].text,
            start_char=idx * 10,
            end_char=idx * 10 + len(all_words[idx].text),
            src_word_indices=(idx,),
        )
        for block in blocks
        for idx in block.child_word_indices
    )
    normalized = NormalizedText(
        text=" ".join(all_words[idx].text for block in blocks
                      for idx in block.child_word_indices),
        spans=spans,
    )
    nlp = NLPResult(provider="stub", tokens=[], confidence=None)
    diacritized = DiacritizationResult(
        provider="stub", diacritized_text="", confidence=None
    )
    g2p = G2PResult(provider="stub", phonemes=[], confidence=None)
    return normalized, blocks, nlp, diacritized, g2p


class TestEconomyPdfTaxonomySmoke:
    def test_at_least_two_question_stem_blocks_detected(self):
        blocks = build_blocks(_ECONOMY_WORDS, _PAGE_STATS)
        qs_blocks = [b for b in blocks if b.block_type == "question_stem"]
        assert len(qs_blocks) >= 1, (
            f"Expected ≥1 question_stem block; got: {[(b.block_id, b.block_type) for b in blocks]}"
        )

    def test_question_stem_text_contains_question_marker(self):
        blocks = build_blocks(_ECONOMY_WORDS, _PAGE_STATS)
        qs_blocks = [b for b in blocks if b.block_type == "question_stem"]
        assert qs_blocks, "No question_stem blocks found"
        # At least one question_stem block must contain "?" or "שאלה"
        question_markers = {"?", "שאלה"}
        found_marker = False
        for block in qs_blocks:
            texts = {_ECONOMY_WORDS[i].text for i in block.child_word_indices}
            if texts & question_markers:
                found_marker = True
                break
        assert found_marker, (
            f"No question_stem block contains '?' or 'שאלה'. Blocks: "
            f"{[(b.block_id, [_ECONOMY_WORDS[i].text for i in b.child_word_indices]) for b in qs_blocks]}"
        )

    def test_full_pipeline_produces_reading_plan_with_question_stem(self):
        """Full pipeline: OCR words → blocks → ReadingPlan with question_stem kind."""
        blocks = build_blocks(_ECONOMY_WORDS, _PAGE_STATS)
        block_tuple = tuple(blocks)
        normalized, block_tuple, nlp, diac, g2p = _build_synthetic_inputs(block_tuple)
        plan = ReadingPlan.from_inputs(
            page_id="economy-p1",
            normalized=normalized,
            blocks=block_tuple,
            nlp_result=nlp,
            diacritization=diac,
            g2p_result=g2p,
        )
        qs_plan_blocks = [b for b in plan.blocks if b.block_kind == "question_stem"]
        assert len(qs_plan_blocks) >= 1, (
            f"ReadingPlan has no question_stem blocks. kinds={[b.block_kind for b in plan.blocks]}"
        )
