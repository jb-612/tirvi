"""F08 T-02 — Tesseract invoker with image_to_data.

Spec: N01/F08 DE-02. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-056, FT-057. BT-anchors: BT-040, BT-041.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestTesseractAdapter:
    def test_us_01_ac_01_ft_056_invokes_pytesseract_image_to_data(self) -> None:
        pass

    def test_us_01_ac_01_ft_057_per_word_conf_normalized_to_0_1(self) -> None:
        # Given: pytesseract returns conf in 0-100 range
        # When:  adapter wraps in OCRWord
        # Then:  conf is normalized to [0.0, 1.0]
        pass

    def test_us_01_ac_01_bt_040_uses_psm_6_lang_heb(self) -> None:
        pass

    def test_us_02_ac_01_bt_041_returns_ocr_result_never_bytes(self) -> None:
        # Given: a happy-path PDF
        # When:  adapter.ocr_pdf(pdf_bytes) is called
        # Then:  isinstance(result, OCRResult); never bytes
        pass
