"""F20 T-04 — Shva quiescent vs vocal classification.

Spec: N02/F20 DE-03. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(
    reason="vocal-shva is inline via predict_vocal_shva=True per ADR-028; "
    "per-token test moot"
)
class TestVocalShva:
    def test_us_01_ac_01_first_position_shva_is_vocal(self) -> None:
        pass

    def test_us_01_ac_01_after_dagesh_is_vocal(self) -> None:
        pass
