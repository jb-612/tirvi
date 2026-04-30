"""F11 T-04 — block bbox aggregation + word coverage.

Spec: N01/F11 DE-04. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestBlockBbox:
    def test_us_01_ac_01_block_bbox_is_union_of_child_words(self) -> None:
        pass

    def test_us_01_ac_01_every_word_in_exactly_one_block(self) -> None:
        # Round-trip invariant: union of child_word_indices = all input words
        pass

    def test_us_01_ac_01_block_id_format_b_n(self) -> None:
        # b1, b2, b3, ...
        pass
