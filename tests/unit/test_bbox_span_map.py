"""F14 T-02 — bbox→span round-trip invariant.

Spec: N02/F14 DE-02. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestBboxSpanMap:
    def test_us_01_ac_01_span_src_word_indices_non_empty(self) -> None:
        pass

    def test_us_01_ac_01_union_of_src_indices_equals_input(self) -> None:
        # Property: every input word appears in exactly one span
        pass
