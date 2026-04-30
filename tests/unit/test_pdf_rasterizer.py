"""F08 T-01 — PDF page rasterizer (300 dpi).

Spec: N01/F08 DE-01. AC: US-01/AC-01. FT-anchors: FT-061.
"""

from __future__ import annotations

import io

import pytest
from PIL import Image

from tirvi.adapters.tesseract.rasterizer import rasterize_pdf
from tirvi.errors import AdapterError


def _one_page_pdf_bytes(width_pt: int = 100, height_pt: int = 100) -> bytes:
    """Build a single-page PDF in memory at 1pt = 1/72 inch via PIL."""
    img = Image.new("RGB", (width_pt, height_pt), "white")
    buf = io.BytesIO()
    # PIL saves at 72 dpi by default → 1 px == 1 pt → page size == width_pt × height_pt pt
    img.save(buf, format="PDF")
    return buf.getvalue()


class TestPDFRasterizer:
    def test_us_01_ac_01_ft_061_rasterizes_at_300_dpi(self) -> None:
        # Given: a single-page PDF whose page is 100 pt × 100 pt
        pdf = _one_page_pdf_bytes(100, 100)

        # When: rasterized at default 300 dpi
        images = rasterize_pdf(pdf)

        # Then: width corresponds to 300 dpi × (100 pt / 72 pt/in) ≈ 417 px (±5)
        assert len(images) == 1
        expected_w = round(100 * 300 / 72)
        assert abs(images[0].width - expected_w) <= 5

    def test_us_01_ac_01_ft_061_one_image_per_page(self) -> None:
        pdf = _one_page_pdf_bytes()
        images = rasterize_pdf(pdf)
        assert len(images) == 1
        assert isinstance(images[0], Image.Image)

    def test_us_01_ac_01_ft_061_corrupt_pdf_raises_typed_error(self) -> None:
        # Given: truncated PDF bytes
        corrupt = b"%PDF-1.4\nthis is not a valid pdf body"

        # When/Then: AdapterError raised (not silent empty, not raw vendor error)
        with pytest.raises(AdapterError):
            rasterize_pdf(corrupt)
