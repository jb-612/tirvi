"""F14 T-03 — line-break rejoin heuristic.

Spec: N02/F14 DE-03. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestLineBreakRejoin:
    def test_us_01_ac_01_rejoins_when_no_sentence_final_punct(self) -> None:
        pass

    def test_us_01_ac_01_does_not_rejoin_across_period(self) -> None:
        pass

    def test_us_01_ac_01_does_not_rejoin_compound_hyphen(self) -> None:
        # Both predicates must hold: no end-punct AND no mid-token hyphen
        pass
