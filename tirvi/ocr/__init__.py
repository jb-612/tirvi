"""tirvi.ocr — OCR result contract layer (F10).

Houses :func:`tirvi.ocr.contracts.assert_ocr_result_v1` (v1 invariant
assertion) and :func:`tirvi.ocr.aggregation.aggregate_lang_hints`
(top-level lang_hints derivation). The frozen result dataclasses live in
:mod:`tirvi.results`; this module adds non-mutating contract + helper
surface around them.
"""

__all__: list[str] = []
