"""F30 T-02 — marks monotonicity invariant.

Spec: N03/F30 DE-04. AC: US-02/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestMarksMonotonic:
    def test_us_02_ac_01_monotonic_marks_pass(self) -> None:
        pass

    def test_us_02_ac_01_non_monotonic_marks_raise_timing_invariant_error(self) -> None:
        pass
