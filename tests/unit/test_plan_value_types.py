"""F22 T-01 — PlanBlock and PlanToken value types.

Spec: N02/F22 DE-02. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPlanValueTypes:
    def test_us_01_ac_01_plan_token_is_frozen(self) -> None:
        pass

    def test_us_01_ac_01_plan_block_is_frozen(self) -> None:
        pass

    def test_us_01_ac_01_plan_token_id_format_block_position(self) -> None:
        # INV-PLAN-T-001: id == "{block_id}-{position}"
        pass

    def test_us_01_ac_01_plan_token_id_byte_identical_across_runs(self) -> None:
        pass
