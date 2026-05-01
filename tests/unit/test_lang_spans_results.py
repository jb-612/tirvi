"""T-01 — LanguageSpan + LanguageSpansResult value types (F16 DE-06)."""

from dataclasses import FrozenInstanceError

import pytest

from tirvi.lang_spans import LanguageSpan, LanguageSpansResult


class TestLanguageSpan:
    def test_construct_with_fields(self):
        span = LanguageSpan(start=0, end=4, lang="he", confidence=1.0)
        assert span.start == 0
        assert span.end == 4
        assert span.lang == "he"
        assert span.confidence == 1.0

    def test_is_frozen(self):
        span = LanguageSpan(start=0, end=1, lang="he", confidence=1.0)
        with pytest.raises(FrozenInstanceError):
            span.start = 5  # type: ignore[misc]

    def test_is_hashable(self):
        span = LanguageSpan(start=0, end=1, lang="he", confidence=1.0)
        assert hash(span) == hash(LanguageSpan(start=0, end=1, lang="he", confidence=1.0))


class TestLanguageSpansResult:
    def test_empty_spans_confidence_is_none(self):
        result = LanguageSpansResult(spans=())
        assert result.spans == ()
        assert result.provider == "tirvi-rules-v1"
        assert result.confidence is None

    def test_single_span_confidence_is_span_confidence(self):
        s = LanguageSpan(start=0, end=4, lang="he", confidence=1.0)
        result = LanguageSpansResult(spans=(s,), confidence=1.0)
        assert result.confidence == 1.0

    def test_multi_span_aggregate_min(self):
        a = LanguageSpan(start=0, end=4, lang="he", confidence=1.0)
        b = LanguageSpan(start=5, end=12, lang="en", confidence=0.85)
        result = LanguageSpansResult(spans=(a, b), confidence=0.85)
        assert result.confidence == 0.85

    def test_default_provider(self):
        result = LanguageSpansResult(spans=())
        assert result.provider == "tirvi-rules-v1"

    def test_is_frozen(self):
        result = LanguageSpansResult(spans=())
        with pytest.raises(FrozenInstanceError):
            result.provider = "other"  # type: ignore[misc]

    def test_is_hashable(self):
        a = LanguageSpan(start=0, end=4, lang="he", confidence=1.0)
        r1 = LanguageSpansResult(spans=(a,), confidence=1.0)
        r2 = LanguageSpansResult(spans=(a,), confidence=1.0)
        assert hash(r1) == hash(r2)
