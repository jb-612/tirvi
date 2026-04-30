"""F08 — TesseractOCRAdapter.ocr_pdf() wiring.

Verifies the adapter composes rasterizer + invoker + layout into an OCRResult.
Vendor packages (pdf2image, pytesseract, PIL) are stubbed in sys.modules so
this test runs locally without the Docker environment.

Spec: N01/F08 DE-01..05. AC: US-01/AC-01.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Vendor stubs — inserted before any tirvi.adapters.tesseract.* import
# so that module-level vendor imports succeed.
# ---------------------------------------------------------------------------
for _mod in ("pdf2image", "pytesseract"):
    sys.modules.setdefault(_mod, MagicMock())

_exc_stub = MagicMock()
_exc_stub.PDFInfoNotInstalledError = type("PDFInfoNotInstalledError", (Exception,), {})
_exc_stub.PDFPageCountError = type("PDFPageCountError", (Exception,), {})
_exc_stub.PDFSyntaxError = type("PDFSyntaxError", (Exception,), {})
sys.modules.setdefault("pdf2image.exceptions", _exc_stub)
sys.modules.setdefault("PIL", MagicMock())
sys.modules.setdefault("PIL.Image", MagicMock())

# Delayed import so stubs are in place first
from tirvi.adapters.tesseract.adapter import TesseractOCRAdapter  # noqa: E402
from tirvi.results import OCRResult, OCRWord  # noqa: E402


def _fake_word(text: str = "שלום") -> OCRWord:
    return OCRWord(text=text, bbox=(0, 0, 50, 20), conf=0.9)


class TestOcrPdfWiring:
    def test_returns_ocr_result(self) -> None:
        img = MagicMock()
        word = _fake_word()
        with (
            patch("tirvi.adapters.tesseract.rasterizer.rasterize_pdf", return_value=[img]),
            patch("tirvi.adapters.tesseract.invoker.invoke_tesseract", return_value=[word]),
            patch("tirvi.adapters.tesseract.layout.reorder_rtl_columns", return_value=[word]),
        ):
            result = TesseractOCRAdapter().ocr_pdf(b"fake-pdf")
        assert isinstance(result, OCRResult)
        assert result.provider == "tesseract"
        assert len(result.pages) == 1
        assert result.pages[0].words == [word]

    def test_passes_dpi_and_lang_to_sub_modules(self) -> None:
        img = MagicMock()
        word = _fake_word()
        with (
            patch("tirvi.adapters.tesseract.rasterizer.rasterize_pdf", return_value=[img]) as mock_rast,
            patch("tirvi.adapters.tesseract.invoker.invoke_tesseract", return_value=[word]) as mock_inv,
            patch("tirvi.adapters.tesseract.layout.reorder_rtl_columns", return_value=[word]),
        ):
            TesseractOCRAdapter(lang="eng", dpi=150).ocr_pdf(b"pdf")
        mock_rast.assert_called_once_with(b"pdf", dpi=150)
        mock_inv.assert_called_once_with(img, lang="eng")

    def test_multi_page_pdf_produces_one_page_per_image(self) -> None:
        imgs = [MagicMock(), MagicMock()]
        word = _fake_word()
        with (
            patch("tirvi.adapters.tesseract.rasterizer.rasterize_pdf", return_value=imgs),
            patch("tirvi.adapters.tesseract.invoker.invoke_tesseract", return_value=[word]),
            patch("tirvi.adapters.tesseract.layout.reorder_rtl_columns", return_value=[word]),
        ):
            result = TesseractOCRAdapter().ocr_pdf(b"multi")
        assert len(result.pages) == 2
