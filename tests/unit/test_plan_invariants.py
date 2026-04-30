"""F22 T-04 — ReadingPlan invariants validator.

Spec: N02/F22 DE-04. AC: US-01/AC-01, US-02/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPlanInvariants:
    def test_us_01_ac_01_token_ids_unique_across_blocks(self) -> None:
        # INV-PLAN-001
        pass

    def test_us_01_ac_01_block_order_matches_reading_order(self) -> None:
        # INV-PLAN-002
        pass

    def test_us_01_ac_01_invariant_violation_raises_plan_invariant_error(self) -> None:
        pass
