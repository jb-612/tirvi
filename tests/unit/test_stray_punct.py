"""F14 T-04 — stray-punctuation repair rule.

Spec: N02/F14 DE-04. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestStrayPunct:
    def test_us_01_ac_01_drops_isolated_punct_tokens(self) -> None:
        pass

    def test_us_01_ac_01_logs_repair_to_repair_log(self) -> None:
        pass
