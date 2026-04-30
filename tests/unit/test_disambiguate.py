"""F18 T-01 — top-1 sense disambiguation.

Spec: N02/F18 DE-01. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestDisambiguate:
    def test_us_01_ac_01_picks_top_candidate(self) -> None:
        pass

    def test_us_01_ac_01_marks_ambiguous_when_margin_below_threshold(self) -> None:
        pass

    def test_us_01_ac_01_env_var_tunes_margin(self) -> None:
        # TIRVI_DISAMBIG_MARGIN
        pass
