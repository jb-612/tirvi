"""F22 T-07 — page.json projection (post-review C4).

Spec: N02/F22 DE-07. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPageJsonProjection:
    def test_us_01_ac_01_to_page_json_returns_dict(self) -> None:
        pass

    def test_us_01_ac_01_words_bbox_from_ocr_result(self) -> None:
        pass

    def test_us_01_ac_01_marks_to_word_index_from_first_src_word(self) -> None:
        # Built by walking plan.blocks[].tokens[] and mapping
        # PlanToken.id → first(src_word_indices)
        pass

    def test_us_01_ac_01_conforms_to_page_schema_json(self) -> None:
        # docs/schemas/page.schema.json
        pass
