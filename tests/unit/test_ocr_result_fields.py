"""F10 — OCRResult field-presence tests.

Spec: N01/F10 DE-01..DE-03. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestOCRResultFields:
    def test_us_01_ac_01_provider_field_required(self) -> None:
        pass

    def test_us_01_ac_01_pages_list_required(self) -> None:
        pass

    def test_us_01_ac_01_per_word_bbox_is_int_4_tuple(self) -> None:
        pass

    def test_us_01_ac_01_confidence_none_default_not_zero(self) -> None:
        # biz S01 — distinguishes "no signal" from "low confidence"
        pass

    def test_us_01_ac_01_per_page_lang_hints_list(self) -> None:
        pass
