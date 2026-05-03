"""F53 T-04 — F23 builder integration with the clause chunker.

The SSML builder calls `chunk_block_tokens` and emits
`<break time="500ms"/>` between fragments. populate_plan_ssml also
updates each PlanBlock's transformations[] with the breaks.

Spec: N02/F53 DE-04. AC: F53-S04/AC-01. ADR-041 row #9.
"""
from __future__ import annotations

from tirvi.plan import ReadingPlan
from tirvi.plan.value_objects import PlanBlock, PlanToken
from tirvi.ssml.builder import (
    build_block_ssml,
    populate_plan_ssml,
)


def _t(text: str, idx: int = 0, pos: str | None = None) -> PlanToken:
    return PlanToken(
        id=f"b1-{idx}", text=text, src_word_indices=(idx,), pos=pos,
    )


def _short_block() -> PlanBlock:
    return PlanBlock(
        block_id="b1", block_kind="paragraph",
        tokens=tuple(_t(f"w{i}", i) for i in range(10)),
    )


def _long_block_with_period() -> PlanBlock:
    """30-token block with a period at index 15 (a safe boundary)."""
    tokens = (
        tuple(_t(f"w{i}", i) for i in range(15))
        + (_t(".", 15),)
        + tuple(_t(f"w{i}", i) for i in range(16, 30))
    )
    return PlanBlock(
        block_id="b1", block_kind="paragraph", tokens=tokens,
    )


def _long_block_no_boundary() -> PlanBlock:
    """30-token block with no punctuation, no SCONJ — chunker skips."""
    return PlanBlock(
        block_id="b1", block_kind="paragraph",
        tokens=tuple(_t(f"word{i}", i) for i in range(30)),
    )


def _plan_with(block: PlanBlock) -> ReadingPlan:
    return ReadingPlan(page_id="p0", blocks=(block,))


class TestBuildBlockSSMLIntraBlockBreaks:
    def test_short_block_has_no_intra_break(self):
        ssml = build_block_ssml(_short_block())
        assert '<break time="500ms"/>' not in ssml
        assert ssml.startswith('<speak xml:lang="he-IL">')

    def test_long_block_with_period_inserts_intra_break(self):
        ssml = build_block_ssml(_long_block_with_period())
        # The break must appear AFTER the period mark and BEFORE the
        # next token's mark.
        assert ssml.count('<break time="500ms"/>') == 1

    def test_long_block_no_boundary_emits_no_break(self):
        # When the chunker can't find a safe boundary, no <break>
        # is emitted; SSML degrades gracefully to the unchunked form.
        ssml = build_block_ssml(_long_block_no_boundary())
        assert '<break time="500ms"/>' not in ssml


class TestPopulatePlanSSMLProvenance:
    def test_long_block_gets_clause_split_provenance(self):
        plan = _plan_with(_long_block_with_period())
        new_plan = populate_plan_ssml(plan)
        block = new_plan.blocks[0]
        assert any(
            t.get("kind") == "clause_split"
            for t in block.transformations
        ), f"expected clause_split entry; got {block.transformations!r}"

    def test_short_block_provenance_unchanged(self):
        block_in = _short_block()
        plan = _plan_with(block_in)
        new_plan = populate_plan_ssml(plan)
        # No chunker breaks added when sentence is under threshold
        block_out = new_plan.blocks[0]
        chunker_breaks = [
            t for t in block_out.transformations
            if t.get("kind", "").startswith("clause_split")
        ]
        assert chunker_breaks == []

    def test_no_boundary_emits_skipped_provenance(self):
        plan = _plan_with(_long_block_no_boundary())
        new_plan = populate_plan_ssml(plan)
        block = new_plan.blocks[0]
        skipped = [
            t for t in block.transformations
            if t.get("kind") == "clause_split_skipped"
        ]
        assert len(skipped) == 1
