"""F19 T-02 — NLP context tilt for homograph picks.

Spec: N02/F19 DE-02. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestNakdanContext:
    def test_us_01_ac_01_pos_context_biases_pick(self) -> None:
        pass

    def test_us_01_ac_01_no_context_falls_through_to_seq2seq(self) -> None:
        pass
