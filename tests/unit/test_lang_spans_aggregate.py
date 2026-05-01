"""T-03 — Run-length aggregation with WS absorption (F16 DE-02)."""

from tirvi.lang_spans.aggregate import aggregate_runs
from tirvi.lang_spans.classify import Script, classify_char
from tirvi.lang_spans.results import LanguageSpan


def _tags(text: str) -> list[Script]:
    return [classify_char(c) for c in text]


class TestAggregateRuns:
    def test_empty_input_returns_empty(self):
        assert aggregate_runs([], "") == []

    def test_all_whitespace_returns_empty(self):
        text = "   "
        assert aggregate_runs(_tags(text), text) == []

    def test_single_hebrew_run(self):
        text = "שלום"
        out = aggregate_runs(_tags(text), text)
        assert out == [LanguageSpan(start=0, end=4, lang="he", confidence=1.0)]

    def test_single_latin_run(self):
        text = "hello"
        out = aggregate_runs(_tags(text), text)
        assert out == [LanguageSpan(start=0, end=5, lang="latin", confidence=1.0)]

    def test_two_adjacent_same_lang_merge_via_ws(self):
        text = "hello world"
        out = aggregate_runs(_tags(text), text)
        # WS absorbed; both Latin spans merge into one
        assert out == [LanguageSpan(start=0, end=11, lang="latin", confidence=1.0)]

    def test_brand_name_microsoft_word_single_en_span(self):
        text = "Microsoft Word"
        out = aggregate_runs(_tags(text), text)
        assert out == [LanguageSpan(start=0, end=14, lang="latin", confidence=1.0)]

    def test_he_then_latin_keeps_two_spans(self):
        text = "ערך hello"  # 3 he + 1 ws + 5 latin
        out = aggregate_runs(_tags(text), text)
        # WS absorbed into prev he span (extends end to 4); latin starts at 4
        assert out == [
            LanguageSpan(start=0, end=4, lang="he", confidence=1.0),
            LanguageSpan(start=4, end=9, lang="latin", confidence=1.0),
        ]

    def test_output_sorted_by_start(self):
        text = "abc שלום xyz"
        out = aggregate_runs(_tags(text), text)
        starts = [s.start for s in out]
        assert starts == sorted(starts)

    def test_leading_whitespace_dropped(self):
        text = "   hello"
        out = aggregate_runs(_tags(text), text)
        assert out == [LanguageSpan(start=3, end=8, lang="latin", confidence=1.0)]

    def test_other_treated_as_ws(self):
        text = "hello@world"  # @ is OTHER
        out = aggregate_runs(_tags(text), text)
        # OTHER absorbed into prev latin; following latin merges
        assert out == [LanguageSpan(start=0, end=11, lang="latin", confidence=1.0)]

    def test_digit_run(self):
        text = "0.05"
        out = aggregate_runs(_tags(text), text)
        # DIGIT then SYMBOL then DIGIT — separate spans (T-06 will unify)
        assert [(s.start, s.end, s.lang) for s in out] == [
            (0, 1, "digit"),
            (1, 2, "symbol"),
            (2, 4, "digit"),
        ]
