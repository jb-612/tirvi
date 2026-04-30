"""F08 T-01 — PDF page rasterizer (300 dpi).

Spec: N01/F08 DE-01. AC: US-01/AC-01. FT-anchors: FT-061.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPDFRasterizer:
    def test_us_01_ac_01_ft_061_rasterizes_at_300_dpi(self) -> None:
        # Given: a single-page Hebrew PDF
        # When:  the rasterizer is invoked
        # Then:  one PIL Image is returned with width corresponding to 300 dpi
        pass

    def test_us_01_ac_01_ft_061_one_image_per_page(self) -> None:
        pass

    def test_us_01_ac_01_ft_061_corrupt_pdf_raises_typed_error(self) -> None:
        # Given: a PDF whose bytes are truncated
        # When:  rasterizer is invoked
        # Then:  tirvi.errors.AdapterError is raised (no silent empty)
        pass
