"""F10 T-03 — OCRResultBuilder.from_yaml fixture builder.

Spec: N01/F10 DE-03. AC: US-02/AC-01. ADR-017 (YAML over Python DSL).
"""

from pathlib import Path

import pytest

from tirvi.errors import SchemaContractError
from tirvi.fixtures.ocr.builder import OCRResultBuilder
from tirvi.results import OCRResult

FIXTURE = Path(__file__).parent.parent / "fixtures" / "ocr" / "sample_he_page.yaml"


class TestOCRResultBuilder:
    def test_us_01_ac_01_from_yaml_returns_ocr_result(self) -> None:
        result = OCRResultBuilder.from_yaml(FIXTURE)
        assert isinstance(result, OCRResult)
        assert result.provider == "tesseract-5.3.4-heb-best"
        assert result.confidence == 0.92
        assert len(result.pages) == 1
        assert len(result.pages[0].words) == 2

    def test_us_01_ac_01_from_yaml_preserves_word_fields(self) -> None:
        result = OCRResultBuilder.from_yaml(FIXTURE)
        word = result.pages[0].words[0]
        assert word.text == "שלום"
        assert word.bbox == (10, 20, 80, 60)
        assert word.confidence == 0.95
        assert word.lang_hint == "he"

    def test_us_01_ac_01_from_yaml_preserves_page_lang_hints(self) -> None:
        result = OCRResultBuilder.from_yaml(FIXTURE)
        assert result.pages[0].lang_hints == ["he"]

    def test_us_01_ac_01_from_yaml_accepts_str_path(self) -> None:
        result = OCRResultBuilder.from_yaml(str(FIXTURE))
        assert isinstance(result, OCRResult)

    def test_us_01_ac_01_from_yaml_validates_schema(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("provider: x\n")  # no pages key
        with pytest.raises(SchemaContractError):
            OCRResultBuilder.from_yaml(bad)

    def test_us_01_ac_01_from_yaml_assert_bbox_int_4_tuple(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad_bbox.yaml"
        bad.write_text(
            "provider: x\n"
            "pages:\n"
            "  - words:\n"
            "      - text: a\n"
            "        bbox: [1, 2, 3]\n"
        )
        with pytest.raises(SchemaContractError):
            OCRResultBuilder.from_yaml(bad)

    def test_us_01_ac_01_from_dict_accepts_pre_parsed(self) -> None:
        data = {
            "provider": "fake",
            "pages": [
                {
                    "lang_hints": ["he"],
                    "words": [
                        {"text": "x", "bbox": [0, 0, 1, 1], "conf": 0.5, "lang_hint": "he"}
                    ],
                }
            ],
        }
        result = OCRResultBuilder.from_dict(data)
        assert result.provider == "fake"
        assert result.pages[0].words[0].text == "x"
        assert result.pages[0].words[0].bbox == (0, 0, 1, 1)
