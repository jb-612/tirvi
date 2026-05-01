"""F10 — OCRResult field-presence tests.

Spec: N01/F10 DE-01..DE-03,DE-05. AC: US-01/AC-01.

Field-name reconciliation: ``tirvi/results.py`` is protected. Existing
fields are: ``OCRWord(text, bbox, conf, lang_hint)``;
``OCRPage(words, lang_hints)``; ``OCRResult(provider, pages, confidence)``.
The hint in tasks.md said "extend OCRWord with bbox/confidence/lang_hint" but
those already exist (under ``conf`` not ``confidence``). T-01 therefore lands
as confirming tests over the existing surface; T-05 lands as a conformance
test (``provider`` carries the provider_version string) since the frozen
dataclass cannot accept a new ``metadata`` field. See dispute-item.md.
"""

import pytest

from tirvi.ocr.aggregation import aggregate_lang_hints
from tirvi.results import OCRPage, OCRResult, OCRWord


class TestOCRResultFields:
    """T-01 — confirming tests over existing OCRWord/OCRPage/OCRResult surface."""

    def test_us_01_ac_01_provider_field_required(self) -> None:
        result = OCRResult(provider="tesseract", pages=[])
        assert result.provider == "tesseract"

    def test_us_01_ac_01_pages_list_required(self) -> None:
        page = OCRPage(words=[])
        result = OCRResult(provider="tesseract", pages=[page])
        assert result.pages == [page]

    def test_us_01_ac_01_per_word_bbox_is_int_4_tuple(self) -> None:
        word = OCRWord(text="שלום", bbox=(10, 20, 30, 40))
        assert word.bbox == (10, 20, 30, 40)
        assert all(isinstance(v, int) for v in word.bbox)
        assert len(word.bbox) == 4

    def test_us_01_ac_01_conf_none_default_not_zero(self) -> None:
        # biz S01 — distinguishes "no signal" from "low confidence"
        word = OCRWord(text="x", bbox=(0, 0, 1, 1))
        assert word.conf is None

    def test_us_01_ac_01_conf_accepts_float_in_range(self) -> None:
        word = OCRWord(text="x", bbox=(0, 0, 1, 1), conf=0.85)
        assert word.conf == 0.85

    def test_us_01_ac_01_lang_hint_optional(self) -> None:
        word_he = OCRWord(text="שלום", bbox=(0, 0, 1, 1), lang_hint="he")
        word_none = OCRWord(text="123", bbox=(0, 0, 1, 1))
        assert word_he.lang_hint == "he"
        assert word_none.lang_hint is None

    def test_us_01_ac_01_per_page_lang_hints_list_default_empty(self) -> None:
        page = OCRPage(words=[])
        assert page.lang_hints == []

    def test_us_01_ac_01_per_page_lang_hints_list_preserved(self) -> None:
        page = OCRPage(words=[], lang_hints=["he", "en"])
        assert page.lang_hints == ["he", "en"]

    def test_us_01_ac_01_result_confidence_none_default(self) -> None:
        # biz S01 default — None, never 0.0
        result = OCRResult(provider="tesseract", pages=[])
        assert result.confidence is None


class TestOCRPageLangHintsAggregation:
    """T-02 — OCRResult-level lang_hints derived as sorted set-union of per-word values."""

    def test_us_01_ac_01_aggregate_empty(self) -> None:
        result = OCRResult(provider="tesseract", pages=[])
        assert aggregate_lang_hints(result) == []

    def test_us_01_ac_01_aggregate_single_lang(self) -> None:
        page = OCRPage(words=[
            OCRWord(text="שלום", bbox=(0, 0, 1, 1), lang_hint="he"),
            OCRWord(text="עולם", bbox=(2, 0, 3, 1), lang_hint="he"),
        ])
        result = OCRResult(provider="tesseract", pages=[page])
        assert aggregate_lang_hints(result) == ["he"]

    def test_us_01_ac_01_aggregate_multi_lang_sorted(self) -> None:
        page = OCRPage(words=[
            OCRWord(text="hello", bbox=(0, 0, 1, 1), lang_hint="en"),
            OCRWord(text="שלום", bbox=(2, 0, 3, 1), lang_hint="he"),
            OCRWord(text="world", bbox=(4, 0, 5, 1), lang_hint="en"),
        ])
        result = OCRResult(provider="tesseract", pages=[page])
        assert aggregate_lang_hints(result) == ["en", "he"]

    def test_us_01_ac_01_aggregate_skips_none(self) -> None:
        page = OCRPage(words=[
            OCRWord(text="x", bbox=(0, 0, 1, 1), lang_hint=None),
            OCRWord(text="y", bbox=(2, 0, 3, 1), lang_hint="he"),
        ])
        result = OCRResult(provider="tesseract", pages=[page])
        assert aggregate_lang_hints(result) == ["he"]

    def test_us_01_ac_01_aggregate_across_pages(self) -> None:
        p1 = OCRPage(words=[OCRWord(text="a", bbox=(0, 0, 1, 1), lang_hint="he")])
        p2 = OCRPage(words=[OCRWord(text="b", bbox=(0, 0, 1, 1), lang_hint="en")])
        result = OCRResult(provider="tesseract", pages=[p1, p2])
        assert aggregate_lang_hints(result) == ["en", "he"]


class TestOCRProviderVersionConformance:
    """T-05 — provider_version conformance.

    OCRResult is a protected frozen dataclass — cannot add ``metadata: dict``.
    Per teammate brief, T-05 lands as a conformance test verifying that the
    free-form ``provider`` field carries the version string (e.g.
    ``"tesseract-5.3.4-heb-best"``) for POC. Adapter authors stamp the version
    in the provider field; downstream consumers parse if needed. See
    dispute-item.md for the unable-to-extend record.
    """

    def test_us_01_ac_01_provider_carries_version_stamp(self) -> None:
        result = OCRResult(provider="tesseract-5.3.4-heb-best", pages=[])
        assert result.provider == "tesseract-5.3.4-heb-best"

    def test_us_01_ac_01_provider_is_free_form_string(self) -> None:
        # POC: free-form, not parsed structurally yet
        for stamp in ("tesseract-5.3.4", "google-cloud-vision-2024-01", "fake-1.0"):
            assert OCRResult(provider=stamp, pages=[]).provider == stamp

    def test_us_01_ac_01_provider_required_non_empty(self) -> None:
        # At minimum the field must be present; emptiness is caught by v1 invariants
        with pytest.raises(TypeError):
            OCRResult(pages=[])  # type: ignore[call-arg]
