"""F11 T-01 — block-type taxonomy (POC scope).

Spec: N01/F11 DE-01. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestBlockTaxonomy:
    def test_us_01_ac_01_block_types_is_3_for_poc(self) -> None:
        # Given: tirvi.blocks.BLOCK_TYPES tuple
        # Then:  exactly heading, paragraph, question_stem
        pass

    def test_us_01_ac_01_out_of_scope_type_raises(self) -> None:
        # POC fails loud on table/figure/math/answer_option
        pass
