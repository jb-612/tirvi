"""TesseractOCRAdapter — :class:`tirvi.ports.OCRBackend` implementation.

Spec: N01/F08. AC: US-01/AC-01.
FT-anchors: FT-061. BT-anchors: BT-040, BT-041.
"""

from tirvi.ports import OCRBackend
from tirvi.results import OCRResult


class TesseractOCRAdapter(OCRBackend):
    """Tesseract-based OCR adapter for Hebrew PDF pages.

    Invariants (named, TDD fills):
      - INV-TESS-001 (FT-061): rasterizes at 300 dpi (post-deskew if enabled)
      - INV-TESS-002 (FT-056, FT-057): per-word ``conf`` normalized to [0.0, 1.0]
      - INV-TESS-003 (BT-040): RTL multi-column page reorder via x-center clustering
      - INV-TESS-004 (BT-041): raises typed error on corrupt PDF (no silent empty)
      - INV-TESS-005 (DE-06, ADR-014): only this module imports vendor SDKs
    """

    def __init__(
        self,
        lang: str = "heb",
        dpi: int = 300,
        deskew: bool = False,
    ) -> None:
        # TODO US-01/AC-01: store config; lazy-init pytesseract (vendor-bound import)
        self._lang = lang
        self._dpi = dpi
        self._deskew = deskew

    def ocr_pdf(self, pdf_bytes: bytes) -> OCRResult:
        # TODO INV-TESS-001 (T-01 PDF page rasterizer): pdf2image at 300 dpi
        # TODO INV-TESS-005 (T-02 Tesseract invoker): pytesseract.image_to_data, psm 6, lang heb
        # TODO INV-TESS-003 (T-03 RTL column reorder): cluster x-centers, sort columns desc
        # TODO INV-TESS-002 (T-04 inline lang_hint): per-word lang detection
        # TODO INV-TESS-004 (T-05): raise tirvi.errors.AdapterError on corrupt PDF
        raise NotImplementedError
