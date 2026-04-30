"""F08 T-01 — PDF page rasterizer (300 dpi).

Spec: N01/F08 DE-01. AC: US-01/AC-01. FT-anchors: FT-061.

Vendor boundary: ``pdf2image`` is allowed only inside ``tirvi.adapters.**``
(DE-06, ADR-014). No vendor types appear in the public signature.
"""

from __future__ import annotations

from pdf2image import convert_from_bytes  # type: ignore[import-not-found]
from pdf2image.exceptions import (  # type: ignore[import-not-found]
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError,
)
from PIL import Image  # type: ignore[import-not-found]

from tirvi.errors import AdapterError


def rasterize_pdf(pdf_bytes: bytes, dpi: int = 300) -> list[Image.Image]:
    """Rasterize each PDF page to a PIL Image at ``dpi`` (default 300).

    Raises :class:`tirvi.errors.AdapterError` on corrupt or unreadable PDFs;
    re-raises :class:`PDFInfoNotInstalledError` (toolchain misconfig — surface
    to the operator unchanged).
    """
    try:
        return convert_from_bytes(pdf_bytes, dpi=dpi)  # type: ignore[no-any-return]
    except PDFInfoNotInstalledError:
        raise
    except (PDFSyntaxError, PDFPageCountError) as exc:
        raise AdapterError(f"corrupt PDF: {exc}") from exc
    except Exception as exc:  # pragma: no cover — vendor surface, defensive
        raise AdapterError(f"PDF rasterization failed: {exc}") from exc
