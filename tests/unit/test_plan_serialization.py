"""F22 T-06 — deterministic JSON serialization.

Spec: N02/F22 DE-06. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPlanSerialization:
    def test_us_01_ac_01_to_json_byte_identical_across_runs(self) -> None:
        # Two runs over same input → identical bytes (basis for content hash)
        pass

    def test_us_01_ac_01_sort_keys_true(self) -> None:
        pass

    def test_us_01_ac_01_ensure_ascii_false_preserves_hebrew(self) -> None:
        pass
