"""F10 T-04 — OCRResult v1 contract invariants.

Spec: N01/F10 DE-04. AC: US-01/AC-01. ADR-014 (contract-test-only versioning).

``assert_ocr_result_v1(result)`` raises :class:`SchemaContractError` on:
- ``confidence`` not in ``[0, 1]`` (and not None)
- per-word ``conf`` not in ``[0, 1]`` (and not None)
- ``lang_hint`` not in ``{"he", "en", None}``
- per-word ``bbox`` not a 4-tuple of ints
"""

import pytest

from tirvi.errors import SchemaContractError
from tirvi.ocr.contracts import assert_ocr_result_v1
from tirvi.results import OCRPage, OCRResult, OCRWord


def _result(words: list[OCRWord], *, confidence: float | None = None) -> OCRResult:
    return OCRResult(
        provider="tesseract-5.3.4",
        pages=[OCRPage(words=words)],
        confidence=confidence,
    )


class TestOCRv1Invariants:
    def test_us_01_ac_01_valid_result_passes(self) -> None:
        result = _result(
            [OCRWord(text="שלום", bbox=(0, 0, 10, 10), confidence=0.9, lang_hint="he")],
            confidence=0.95,
        )
        assert_ocr_result_v1(result)  # no raise

    def test_us_01_ac_01_empty_pages_passes(self) -> None:
        assert_ocr_result_v1(OCRResult(provider="x", pages=[]))

    def test_us_01_ac_01_confidence_none_passes(self) -> None:
        # biz S01 — None is the canonical "no signal" value
        assert_ocr_result_v1(_result([], confidence=None))

    def test_us_01_ac_01_confidence_above_one_raises(self) -> None:
        with pytest.raises(SchemaContractError):
            assert_ocr_result_v1(_result([], confidence=1.5))

    def test_us_01_ac_01_confidence_negative_raises(self) -> None:
        with pytest.raises(SchemaContractError):
            assert_ocr_result_v1(_result([], confidence=-0.1))

    def test_us_01_ac_01_word_conf_out_of_range_raises(self) -> None:
        with pytest.raises(SchemaContractError):
            assert_ocr_result_v1(_result(
                [OCRWord(text="x", bbox=(0, 0, 1, 1), confidence=2.0)]
            ))

    def test_us_01_ac_01_word_conf_none_passes(self) -> None:
        assert_ocr_result_v1(_result(
            [OCRWord(text="x", bbox=(0, 0, 1, 1), confidence=None)]
        ))

    def test_us_01_ac_01_lang_hint_unknown_raises(self) -> None:
        with pytest.raises(SchemaContractError):
            assert_ocr_result_v1(_result(
                [OCRWord(text="x", bbox=(0, 0, 1, 1), lang_hint="fr")]
            ))

    def test_us_01_ac_01_lang_hint_none_passes(self) -> None:
        assert_ocr_result_v1(_result(
            [OCRWord(text="x", bbox=(0, 0, 1, 1), lang_hint=None)]
        ))

    def test_us_01_ac_01_bbox_wrong_arity_raises(self) -> None:
        # bbox tuples must be 4-element. The dataclass type hint isn't runtime
        # enforced, so v1 validates structurally.
        bad = OCRWord(text="x", bbox=(0, 0, 1))  # type: ignore[arg-type]
        with pytest.raises(SchemaContractError):
            assert_ocr_result_v1(_result([bad]))

    def test_us_01_ac_01_bbox_non_int_raises(self) -> None:
        bad = OCRWord(text="x", bbox=(0.0, 0, 1, 1))  # type: ignore[arg-type]
        with pytest.raises(SchemaContractError):
            assert_ocr_result_v1(_result([bad]))

    def test_us_01_ac_01_provider_must_be_non_empty_string(self) -> None:
        with pytest.raises(SchemaContractError):
            assert_ocr_result_v1(OCRResult(provider="", pages=[]))
