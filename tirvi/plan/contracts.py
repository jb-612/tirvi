"""F22 — ReadingPlan invariant validator.

Spec: N02/F22 DE-04. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-169. BT-anchors: BT-116.

``assert_plan_v1(plan)`` raises :class:`tirvi.plan.PlanInvariantError`
if any structural invariant is violated; returns ``None`` otherwise.
"""

from collections import Counter

from .aggregates import ReadingPlan
from .errors import PlanInvariantError


def assert_plan_v1(plan: ReadingPlan) -> None:
    """Validate the structural invariants of a ReadingPlan.

    Invariants checked:
      - INV-PLAN-001 (FT-169): every PlanToken.id is unique across all blocks
      - INV-PLAN-001-block (FT-169): every block_id is unique
      - INV-PLAN-PARTITION (BT-116): every src_word_index appears in at
        most one block (no overlap; the partition's coverage of the
        page word list is enforced upstream by F11, not here)

    Raises :class:`PlanInvariantError` on any violation.
    """
    _assert_unique_block_ids(plan)
    _assert_unique_token_ids(plan)
    _assert_word_index_partition(plan)


def _assert_unique_block_ids(plan: ReadingPlan) -> None:
    counts = Counter(b.block_id for b in plan.blocks)
    duplicates = [bid for bid, n in counts.items() if n > 1]
    if duplicates:
        raise PlanInvariantError(
            f"INV-PLAN-001-block: duplicate block_id(s): {duplicates}"
        )


def _assert_unique_token_ids(plan: ReadingPlan) -> None:
    all_token_ids = [t.id for b in plan.blocks for t in b.tokens]
    counts = Counter(all_token_ids)
    duplicates = [tid for tid, n in counts.items() if n > 1]
    if duplicates:
        raise PlanInvariantError(
            f"INV-PLAN-001: duplicate token id(s) across blocks: {duplicates}"
        )


def _assert_word_index_partition(plan: ReadingPlan) -> None:
    seen_in: dict[int, str] = {}
    for block in plan.blocks:
        for token in block.tokens:
            for word_index in token.src_word_indices:
                if word_index in seen_in and seen_in[word_index] != block.block_id:
                    raise PlanInvariantError(
                        f"INV-PLAN-PARTITION: word_index {word_index} appears "
                        f"in both block {seen_in[word_index]!r} and "
                        f"block {block.block_id!r}"
                    )
                seen_in[word_index] = block.block_id
