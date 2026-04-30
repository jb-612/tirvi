"""OCRResultBuilder — YAML-backed canonical OCRResult fixture builder.

Spec: N01/F10. AC: US-01/AC-01. FT-anchors: FT-005, FT-007.
"""

from pathlib import Path

from tirvi.results import OCRResult


class OCRResultBuilder:
    """Constructs :class:`OCRResult` from canonical YAML fixtures.

    Invariants (named, TDD fills):
      - INV-OCR-BUILDER-001 (DE-04, FT-005): YAML schema validated on load
      - INV-OCR-BUILDER-002 (DE-02): per-word ``bbox`` is integer pixel coords
      - INV-OCR-BUILDER-003 (DE-03): per-word ``conf`` in [0.0, 1.0] or None
      - INV-OCR-BUILDER-004 (DE-05): per-page ``lang_hints`` list preserved
    """

    @classmethod
    def from_yaml(cls, path: Path | str) -> OCRResult:
        # TODO US-01/AC-01: parse YAML; validate against schema; build OCRResult
        # TODO INV-OCR-BUILDER-002: assert bbox tuples are int 4-tuples
        # TODO INV-OCR-BUILDER-003: assert conf is float|None, never 0.0 default
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> OCRResult:
        # TODO US-01/AC-01: same as from_yaml but accepts pre-parsed dict
        raise NotImplementedError
