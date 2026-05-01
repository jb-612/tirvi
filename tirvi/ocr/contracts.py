"""F10 T-04 — OCRResult v1 contract invariants.

``assert_ocr_result_v1(result)`` validates the structural invariants of a
v1 ``OCRResult`` and raises :class:`tirvi.errors.SchemaContractError` on any
violation. Used inside ``assert_adapter_contract`` (F03 DE-05) and by
fixture-builder validation paths.
"""

from tirvi.errors import SchemaContractError
from tirvi.results import OCRResult, OCRWord

_ALLOWED_LANG_HINTS: frozenset[str | None] = frozenset({"he", "en", None})


def assert_ocr_result_v1(result: OCRResult) -> None:
    """Raise :class:`SchemaContractError` if ``result`` violates v1 invariants."""
    _check_provider(result.provider)
    _check_confidence(result.confidence, "result.confidence")
    for p_idx, page in enumerate(result.pages):
        for w_idx, word in enumerate(page.words):
            _check_word(word, p_idx, w_idx)


def _check_provider(provider: str) -> None:
    if not isinstance(provider, str) or not provider:
        raise SchemaContractError("provider must be a non-empty string")


def _check_confidence(value: float | None, label: str) -> None:
    if value is None:
        return
    if not isinstance(value, (int, float)) or not (0.0 <= float(value) <= 1.0):
        raise SchemaContractError(f"{label} must be in [0, 1] or None")


def _check_word(word: OCRWord, p_idx: int, w_idx: int) -> None:
    loc = f"pages[{p_idx}].words[{w_idx}]"
    _check_confidence(word.confidence, f"{loc}.confidence")
    if word.lang_hint not in _ALLOWED_LANG_HINTS:
        raise SchemaContractError(
            f"{loc}.lang_hint must be one of 'he', 'en', or None"
        )
    _check_bbox(word.bbox, loc)


def _check_bbox(bbox: object, loc: str) -> None:
    if not isinstance(bbox, tuple) or len(bbox) != 4:
        raise SchemaContractError(f"{loc}.bbox must be a 4-tuple")
    if not all(_is_pixel_int(v) for v in bbox):
        raise SchemaContractError(f"{loc}.bbox must contain integer pixel coords")


def _is_pixel_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
