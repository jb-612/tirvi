"""F19 T-04 — Skip filter for non-Hebrew / numeric / punct tokens.

Spec: N02/F19 DE-04. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestTokenSkipFilter:
    def test_us_01_ac_01_skips_non_hebrew_tokens(self) -> None:
        pass

    def test_us_01_ac_01_skips_numeric_tokens(self) -> None:
        pass

    def test_us_01_ac_01_skips_punctuation_tokens(self) -> None:
        pass
