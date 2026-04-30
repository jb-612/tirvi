"""F23 T-02 — per-token <mark> emission.

Spec: N02/F23 DE-02. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPerWordMark:
    def test_us_01_ac_01_every_token_gets_mark_pre_emit(self) -> None:
        pass

    def test_us_01_ac_01_mark_name_matches_plan_token_id(self) -> None:
        # INV-SSML-005: format {block_id}-{position}, e.g., "b3-0"
        pass

    def test_us_01_ac_01_mark_count_equals_token_count(self) -> None:
        pass
