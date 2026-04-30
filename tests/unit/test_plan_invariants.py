"""F22 T-04 — ReadingPlan invariants validator.

Spec: N02/F22 DE-04. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-169. BT-anchors: BT-116.

``assert_plan_v1(plan)`` checks the structural invariants:
  - unique block_ids (INV-PLAN-001 supports)
  - unique token ids across all blocks (INV-PLAN-001)
  - every src_word_index appears in at most one block (no overlap;
    partition without total-word-count requirement for POC)
"""

import pytest

from tirvi.plan import PlanBlock, PlanInvariantError, PlanToken, ReadingPlan
from tirvi.plan.contracts import assert_plan_v1


def _valid_plan() -> ReadingPlan:
    return ReadingPlan(
        page_id="page-1",
        blocks=(
            PlanBlock(
                block_id="b1",
                block_type="heading",
                tokens=(
                    PlanToken(id="b1-0", text="שלום", src_word_indices=(0,)),
                    PlanToken(id="b1-1", text="עולם", src_word_indices=(1,)),
                ),
            ),
            PlanBlock(
                block_id="b2",
                block_type="paragraph",
                tokens=(
                    PlanToken(id="b2-0", text="פרק", src_word_indices=(2,)),
                ),
            ),
        ),
    )


class TestPlanInvariants:
    def test_us_01_ac_01_ft_169_valid_plan_does_not_raise(self) -> None:
        # Given: a well-formed ReadingPlan
        # When:  assert_plan_v1 runs
        # Then:  no exception is raised
        assert_plan_v1(_valid_plan())  # no raise

    def test_us_01_ac_01_ft_169_token_ids_unique_across_blocks(self) -> None:
        # Given: a plan where two tokens share the same id (across blocks)
        # When:  assert_plan_v1 runs
        # Then:  PlanInvariantError is raised
        bad = ReadingPlan(
            page_id="page-1",
            blocks=(
                PlanBlock(
                    block_id="b1",
                    block_type="heading",
                    tokens=(PlanToken(id="dup", text="שלום", src_word_indices=(0,)),),
                ),
                PlanBlock(
                    block_id="b2",
                    block_type="paragraph",
                    tokens=(PlanToken(id="dup", text="עולם", src_word_indices=(1,)),),
                ),
            ),
        )
        with pytest.raises(PlanInvariantError, match="token id"):
            assert_plan_v1(bad)

    def test_us_01_ac_01_ft_169_block_ids_unique(self) -> None:
        # Given: a plan with two blocks sharing the same block_id
        # When:  assert_plan_v1 runs
        # Then:  PlanInvariantError is raised
        bad = ReadingPlan(
            page_id="page-1",
            blocks=(
                PlanBlock(block_id="b1", block_type="heading", tokens=()),
                PlanBlock(block_id="b1", block_type="paragraph", tokens=()),
            ),
        )
        with pytest.raises(PlanInvariantError, match="block_id"):
            assert_plan_v1(bad)

    def test_us_01_ac_01_bt_116_overlapping_word_indices_raise(self) -> None:
        # Given: word index 0 appears in tokens across two different blocks
        # When:  assert_plan_v1 runs
        # Then:  PlanInvariantError is raised (no partition violation)
        bad = ReadingPlan(
            page_id="page-1",
            blocks=(
                PlanBlock(
                    block_id="b1",
                    block_type="heading",
                    tokens=(PlanToken(id="b1-0", text="א", src_word_indices=(0,)),),
                ),
                PlanBlock(
                    block_id="b2",
                    block_type="paragraph",
                    tokens=(PlanToken(id="b2-0", text="ב", src_word_indices=(0,)),),
                ),
            ),
        )
        with pytest.raises(PlanInvariantError, match="word_index"):
            assert_plan_v1(bad)

    def test_us_02_ac_01_empty_blocks_are_valid(self) -> None:
        # Given: a plan with an empty-tokens block (DE-05 empty-block skip path)
        # When:  assert_plan_v1 runs
        # Then:  no exception is raised — empty blocks are legitimate
        plan = ReadingPlan(
            page_id="page-1",
            blocks=(
                PlanBlock(block_id="b1", block_type="heading", tokens=()),
                PlanBlock(
                    block_id="b2",
                    block_type="paragraph",
                    tokens=(PlanToken(id="b2-0", text="א", src_word_indices=(0,)),),
                ),
            ),
        )
        assert_plan_v1(plan)
