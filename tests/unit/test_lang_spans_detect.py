"""T-07 — detect_language_spans pipeline + smoke (F16 DE-06/07)."""

from tirvi.lang_spans import LanguageSpan, LanguageSpansResult, detect_language_spans


class TestDetectLanguageSpans:
    def test_returns_language_spans_result(self):
        result = detect_language_spans("שלום")
        assert isinstance(result, LanguageSpansResult)
        assert result.provider == "tirvi-rules-v1"

    def test_empty_input_yields_empty_spans_and_none_confidence(self):
        result = detect_language_spans("")
        assert result.spans == ()
        assert result.confidence is None

    def test_pure_hebrew_single_he_span(self):
        text = "שלום עולם"
        result = detect_language_spans(text)
        assert len(result.spans) == 1
        assert result.spans[0].lang == "he"
        assert result.confidence == 1.0

    def test_pure_english_single_en_span(self):
        text = "Microsoft Word"
        result = detect_language_spans(text)
        assert len(result.spans) == 1
        assert result.spans[0].lang == "en"

    def test_biz_example_he_en_he_num(self):
        # FT-112 fixture
        text = "ערך p-value הוא 0.05"
        result = detect_language_spans(text)
        langs = [s.lang for s in result.spans]
        assert langs == ["he", "en", "he", "num"]

    def test_aggregate_confidence_is_min_of_span_confidences(self):
        text = "ערך p-value הוא 0.05"
        result = detect_language_spans(text)
        expected = min(s.confidence for s in result.spans)
        assert result.confidence == expected
        assert result.confidence == 0.85  # the en span via hyphen-bridge

    def test_deterministic_same_input_same_output(self):
        text = "ערך p-value הוא 0.05"
        a = detect_language_spans(text)
        b = detect_language_spans(text)
        assert a == b
        assert hash(a) == hash(b)

    def test_single_latin_in_hebrew_merges_to_he(self):
        # FT-113 — single Latin inside Hebrew word
        text = "שלוםaעולם"
        result = detect_language_spans(text)
        assert len(result.spans) == 1
        assert result.spans[0].lang == "he"
        assert result.spans[0].confidence == 0.85

    def test_spans_sorted_by_start(self):
        text = "abc שלום 123"
        result = detect_language_spans(text)
        starts = [s.start for s in result.spans]
        assert starts == sorted(starts)

    def test_returns_tuple_for_spans(self):
        result = detect_language_spans("שלום")
        assert isinstance(result.spans, tuple)
        # all elements LanguageSpan
        assert all(isinstance(s, LanguageSpan) for s in result.spans)
