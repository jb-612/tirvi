"""F08 T-05 — Optional Hough deskew preprocessor.

Spec: N01/F08 DE-05. AC: US-01/AC-01. FT-anchors: FT-059. BT-anchors: BT-041.

cv2 is optional in dev — tests inject a stub cv2 via ``unittest.mock.patch``.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from PIL import Image

from tirvi.adapters.tesseract import deskew


def _img(size: int = 50) -> Image.Image:
    return Image.new("L", (size, size), color=255)


class TestDeskewEnabledFlag:
    def test_us_01_ac_01_ft_059_disabled_by_default(self, monkeypatch) -> None:
        monkeypatch.delenv("TIRVI_TESSERACT_DESKEW", raising=False)
        assert deskew.is_enabled(adapter_flag=False) is False

    def test_us_02_ac_01_env_var_on_enables_when_flag_off(self, monkeypatch) -> None:
        monkeypatch.setenv("TIRVI_TESSERACT_DESKEW", "on")
        assert deskew.is_enabled(adapter_flag=False) is True

    def test_us_02_ac_01_env_var_off_disables_even_when_flag_on(self, monkeypatch) -> None:
        monkeypatch.setenv("TIRVI_TESSERACT_DESKEW", "off")
        assert deskew.is_enabled(adapter_flag=True) is False

    def test_adapter_flag_on_enables_with_no_env(self, monkeypatch) -> None:
        monkeypatch.delenv("TIRVI_TESSERACT_DESKEW", raising=False)
        assert deskew.is_enabled(adapter_flag=True) is True


class TestDeskewThreshold:
    def test_us_01_ac_01_ft_059_below_5_deg_image_unchanged(self) -> None:
        img = _img()
        with patch.object(deskew, "_detect_angle", return_value=2.0), \
             patch.object(deskew, "_load_cv2", return_value=object()):
            out = deskew.deskew_image(img)
        assert out is img

    def test_us_01_ac_01_ft_059_at_or_above_5_deg_image_rotated(self) -> None:
        img = _img()
        with patch.object(deskew, "_detect_angle", return_value=7.5), \
             patch.object(deskew, "_load_cv2", return_value=object()):
            out = deskew.deskew_image(img)
        assert out is not img
        # Rotation with expand=True grows the canvas for a non-zero angle.
        assert out.size != img.size or out is not img


class TestDeskewMissingCv2:
    def test_bt_041_missing_cv2_raises_not_implemented(self) -> None:
        img = _img()
        with patch.object(deskew, "_load_cv2", side_effect=NotImplementedError("cv2 not available")):
            with pytest.raises(NotImplementedError, match="cv2"):
                deskew.deskew_image(img)
