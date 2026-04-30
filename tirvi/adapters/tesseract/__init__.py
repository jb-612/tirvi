"""F08 — Tesseract OCR adapter.

Implements :class:`tirvi.ports.OCRBackend` using ``pytesseract`` + ``pdf2image``
(or ``pypdfium2``) for PDF rasterization. Optional Hough-based deskew via
``opencv-python`` (env-controlled, 5° threshold per ADR-016).

Vendor isolation: this module is the only place ``pytesseract``, ``pdf2image``,
``pypdfium2``, and ``cv2`` may be imported (DE-06, ADR-014, ruff banned-api).

Public API filled at L5; this file is a vendor-boundary anchor for L1.

Spec: N01/F08. Bounded context: ``bc:extraction``.
"""

__all__: list[str] = []
