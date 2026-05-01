"""OCRResultBuilder — YAML-backed canonical OCRResult fixture builder.

Spec: N01/F10. AC: US-01/AC-01. FT-anchors: FT-005, FT-007.
"""

from pathlib import Path
from typing import Any

import yaml

from tirvi.errors import SchemaContractError
from tirvi.ocr.contracts import assert_ocr_result_v1
from tirvi.results import OCRPage, OCRResult, OCRWord


class OCRResultBuilder:
    """Constructs :class:`OCRResult` from canonical YAML fixtures."""

    @classmethod
    def from_yaml(cls, path: Path | str) -> OCRResult:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            raise SchemaContractError("OCR fixture root must be a mapping")
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OCRResult:
        if "provider" not in data or "pages" not in data:
            raise SchemaContractError("OCR fixture missing 'provider' or 'pages'")
        pages = [_build_page(p) for p in data["pages"]]
        result = OCRResult(
            provider=data["provider"],
            pages=pages,
            confidence=data.get("confidence"),
        )
        assert_ocr_result_v1(result)
        return result


def _build_page(raw: dict[str, Any]) -> OCRPage:
    words = [_build_word(w) for w in raw.get("words", [])]
    return OCRPage(words=words, lang_hints=list(raw.get("lang_hints", [])))


def _build_word(raw: dict[str, Any]) -> OCRWord:
    bbox = raw.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4:
        raise SchemaContractError("word.bbox must be a 4-element list")
    return OCRWord(
        text=raw["text"],
        bbox=tuple(bbox),  # type: ignore[arg-type]
        confidence=raw.get("confidence"),
        lang_hint=raw.get("lang_hint"),
    )
