"""F08 T-02 — Tesseract invoker with image_to_data.

Spec: N01/F08 DE-02. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-056, FT-057. BT-anchors: BT-040, BT-041.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from PIL import Image

from tirvi.adapters.tesseract.invoker import invoke_tesseract


def _empty_data() -> dict[str, list[object]]:
    return {
        "level": [],
        "left": [],
        "top": [],
        "width": [],
        "height": [],
        "conf": [],
        "text": [],
    }


def _one_word(text: str = "שלום", conf: int = 75) -> dict[str, list[object]]:
    return {
        "level": [5],
        "left": [10],
        "top": [20],
        "width": [30],
        "height": [40],
        "conf": [conf],
        "text": [text],
    }


class TestTesseractAdapter:
    def test_us_01_ac_01_ft_056_invokes_pytesseract_image_to_data(self) -> None:
        img = Image.new("RGB", (50, 50), "white")
        with patch(
            "tirvi.adapters.tesseract.invoker.pytesseract.image_to_data",
            return_value=_empty_data(),
        ) as mock:
            invoke_tesseract(img)
        mock.assert_called_once()

    def test_us_01_ac_01_ft_057_per_word_conf_normalized_to_0_1(self) -> None:
        img = Image.new("RGB", (50, 50), "white")
        with patch(
            "tirvi.adapters.tesseract.invoker.pytesseract.image_to_data",
            return_value=_one_word(conf=75),
        ):
            words = invoke_tesseract(img)
        assert len(words) == 1
        assert words[0].confidence == pytest.approx(0.75)
        assert words[0].text == "שלום"
        assert words[0].bbox == (10, 20, 40, 60)

    def test_us_01_ac_01_bt_040_uses_psm_6_lang_heb(self) -> None:
        img = Image.new("RGB", (50, 50), "white")
        with patch(
            "tirvi.adapters.tesseract.invoker.pytesseract.image_to_data",
            return_value=_empty_data(),
        ) as mock:
            invoke_tesseract(img)
        kwargs = mock.call_args.kwargs
        assert kwargs.get("lang") == "heb"
        config = kwargs.get("config", "")
        assert "psm 6" in config

    def test_filters_non_word_levels_and_negative_conf(self) -> None:
        # Tesseract emits page/block/para/line entries (level < 5) and confidence=-1
        # placeholders for missed words; only level==5 with conf >= 0 are real words.
        img = Image.new("RGB", (50, 50), "white")
        data: dict[str, list[object]] = {
            "level": [1, 5, 5],
            "left": [0, 10, 50],
            "top": [0, 20, 60],
            "width": [100, 30, 30],
            "height": [100, 40, 40],
            "conf": [-1, 80, -1],
            "text": ["", "מילה", ""],
        }
        with patch(
            "tirvi.adapters.tesseract.invoker.pytesseract.image_to_data",
            return_value=data,
        ):
            words = invoke_tesseract(img)
        assert len(words) == 1
        assert words[0].text == "מילה"

    @pytest.mark.skip(reason="F08 T-06 deferred per POC-CRITICAL-PATH")
    def test_us_02_ac_01_bt_041_returns_ocr_result_never_bytes(self) -> None:
        pass
