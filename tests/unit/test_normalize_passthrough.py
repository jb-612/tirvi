"""F14 T-01 — pure pass-through normalization.

Spec: N02/F14 DE-01. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestNormalizePassthrough:
    def test_us_01_ac_01_clean_text_unchanged(self) -> None:
        pass

    def test_us_01_ac_01_preserves_nfd_nikud(self) -> None:
        pass
