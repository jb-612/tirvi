"""F20 T-05 — G2P skip filter for non-vocalizable tokens.

Spec: N02/F20 DE-04. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestG2PSkipFilter:
    def test_us_01_ac_01_skips_punctuation(self) -> None:
        pass

    def test_us_01_ac_01_skips_numeric_tokens(self) -> None:
        pass
