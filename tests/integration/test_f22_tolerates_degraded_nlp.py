"""F26 T-10 — F22 reading-plan tolerance assertion (cross-feature).

Spec: N02/F26 DE-05 (verifies degraded contract). AC: US-01/AC-01.

Pins ADR-027's "no worse than current ``_StubNLP`` baseline" claim:
``ReadingPlan.from_inputs`` must accept a degraded NLPResult (no
tokens) without raising, and produce non-empty PlanBlocks where each
PlanToken's NLP-derived fields default to ``None``.
"""

from __future__ import annotations

from tirvi.blocks.value_objects import Block
from tirvi.normalize import NormalizedText, Span
from tirvi.plan.aggregates import ReadingPlan
from tirvi.results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
)


def _build_inputs():
    spans = (
        Span(text="שלום", start_char=0, end_char=4, src_word_indices=(0,)),
        Span(text="עולם", start_char=5, end_char=9, src_word_indices=(1,)),
    )
    normalized = NormalizedText(text="שלום עולם", spans=spans)
    block = Block(
        block_id="b0",
        block_type="paragraph",
        child_word_indices=(0, 1),
        bbox=(10, 20, 100, 40),
    )
    return spans, normalized, (block,)


def test_reading_plan_tolerates_degraded_nlp_result() -> None:
    _, normalized, blocks = _build_inputs()
    degraded = NLPResult(provider="degraded", tokens=[], confidence=None)
    plan = ReadingPlan.from_inputs(
        page_id="p0",
        blocks=blocks,
        normalized=normalized,
        nlp_result=degraded,
        diacritization=DiacritizationResult(
            provider="degraded", diacritized_text="", confidence=None
        ),
        g2p_result=G2PResult(provider="degraded", phonemes=[], confidence=None),
    )

    assert len(plan.blocks) == 1
    assert plan.blocks[0].bbox == (10, 20, 100, 40)
    tokens = plan.blocks[0].tokens
    assert len(tokens) > 0
    for token in tokens:
        assert token.text  # valid text from the source span
        assert token.pos is None
        assert token.lemma is None
        assert token.diacritized_text is None
