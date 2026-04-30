"""F17 T-04 — per-attribute confidence on NLPToken.

Spec: N02/F17 DE-04. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPerAttrConfidence:
    def test_us_01_ac_01_pos_carries_confidence(self) -> None:
        pass

    def test_us_01_ac_01_lemma_carries_confidence(self) -> None:
        pass

    def test_us_01_ac_01_confidence_none_not_zero_default(self) -> None:
        pass
