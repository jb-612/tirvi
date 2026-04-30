"""F22 T-05 — empty-block skip.

Spec: N02/F22 DE-05. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestEmptyBlockSkip:
    def test_us_01_ac_01_blocks_with_zero_tokens_filtered(self) -> None:
        pass

    def test_us_01_ac_01_block_order_preserved_after_skip(self) -> None:
        pass
