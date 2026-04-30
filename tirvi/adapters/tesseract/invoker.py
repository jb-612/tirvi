"""F08 T-02 — Tesseract invoker (``pytesseract.image_to_data``).

Spec: N01/F08 DE-02. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-056, FT-057. BT-anchors: BT-040.

Vendor boundary: ``pytesseract`` is allowed only inside ``tirvi.adapters.**``
(DE-06, ADR-014). Returns :class:`tirvi.results.OCRWord` — never raw vendor
dicts (BT-009).
"""

from __future__ import annotations

from typing import Any

import pytesseract  # type: ignore[import-not-found]
from PIL import Image  # type: ignore[import-not-found]

from tirvi.results import OCRWord


def invoke_tesseract(
    image: Image.Image,
    lang: str = "heb",
    psm: int = 6,
) -> list[OCRWord]:
    """Run Tesseract on a single page image, return one :class:`OCRWord` per
    word-level entry whose confidence is non-negative.
    """
    config = f"--psm {psm}"
    raw: dict[str, list[Any]] = pytesseract.image_to_data(
        image,
        lang=lang,
        config=config,
        output_type=pytesseract.Output.DICT,
    )
    return _to_words(raw)


def _to_words(raw: dict[str, list[Any]]) -> list[OCRWord]:
    words: list[OCRWord] = []
    for i in range(len(raw["level"])):
        word = _maybe_word(raw, i)
        if word is not None:
            words.append(word)
    return words


def _maybe_word(raw: dict[str, list[Any]], i: int) -> OCRWord | None:
    if int(raw["level"][i]) != 5:
        return None
    conf_raw = float(raw["conf"][i])
    if conf_raw < 0:
        return None
    text = str(raw["text"][i])
    if not text.strip():
        return None
    left = int(raw["left"][i])
    top = int(raw["top"][i])
    width = int(raw["width"][i])
    height = int(raw["height"][i])
    return OCRWord(
        text=text,
        bbox=(left, top, left + width, top + height),
        conf=conf_raw / 100.0,
    )
