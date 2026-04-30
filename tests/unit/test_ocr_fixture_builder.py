"""F10 T-04 — OCRResultBuilder.from_yaml fixture builder.

Spec: N01/F10 DE-04. AC: US-01/AC-01. ADR-017 (YAML over Python DSL).
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestOCRResultBuilder:
    def test_us_01_ac_01_from_yaml_returns_ocr_result(self) -> None:
        pass

    def test_us_01_ac_01_from_yaml_validates_schema(self) -> None:
        pass

    def test_us_01_ac_01_from_yaml_assert_bbox_int_4_tuple(self) -> None:
        pass

    def test_us_01_ac_01_from_dict_accepts_pre_parsed(self) -> None:
        pass
