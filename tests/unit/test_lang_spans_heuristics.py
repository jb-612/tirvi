"""T-04/T-05/T-06 — Heuristic rules over aggregated spans (F16 DE-03/04/05)."""

from tirvi.lang_spans.aggregate import aggregate_runs
from tirvi.lang_spans.classify import classify_char
from tirvi.lang_spans.heuristics import (
    apply_hyphen_bridge_rule,
    apply_num_unification,
    apply_transliteration_rule,
)
from tirvi.lang_spans.results import LanguageSpan


def _spans(text: str) -> list[LanguageSpan]:
    return aggregate_runs([classify_char(c) for c in text], text)


# ---------------------------------------------------------------------------
# T-04 — Transliteration rule
# ---------------------------------------------------------------------------


class TestTransliterationRule:
    def test_single_latin_inside_hebrew_merges_to_he(self):
        # Hebrew (3) + latin (1, 'a') + Hebrew (3)
        text = "שלוםaעולם"
        spans = _spans(text)
        out = apply_transliteration_rule(spans, text)
        assert len(out) == 1
        assert out[0].lang == "he"
        assert out[0].start == 0
        assert out[0].end == len(text)
        assert out[0].confidence == 0.85

    def test_multi_latin_inside_hebrew_not_reclassified(self):
        text = "שלוםabעולם"
        spans = _spans(text)
        out = apply_transliteration_rule(spans, text)
        # 2-char latin → not transliteration
        assert len(out) == 3
        assert [s.lang for s in out] == ["he", "latin", "he"]

    def test_single_latin_with_only_left_he_unchanged(self):
        text = "שלוםa"
        spans = _spans(text)
        out = apply_transliteration_rule(spans, text)
        assert [s.lang for s in out] == ["he", "latin"]

    def test_no_he_neighbours_unchanged(self):
        text = "abc"
        spans = _spans(text)
        out = apply_transliteration_rule(spans, text)
        assert out == spans

    def test_empty_input(self):
        assert apply_transliteration_rule([], "") == []


# ---------------------------------------------------------------------------
# T-05 — Hyphen-bridge rule
# ---------------------------------------------------------------------------


class TestHyphenBridgeRule:
    def test_p_dash_value_merges_to_en(self):
        text = "p-value"
        spans = _spans(text)
        # raw: latin, symbol, latin
        out = apply_hyphen_bridge_rule(spans, text)
        assert len(out) == 1
        assert out[0].lang == "en"
        assert out[0].start == 0
        assert out[0].end == 7
        assert out[0].confidence == 0.85

    def test_idempotent(self):
        text = "p-value"
        spans = _spans(text)
        once = apply_hyphen_bridge_rule(spans, text)
        twice = apply_hyphen_bridge_rule(once, text)
        assert once == twice

    def test_standalone_hyphen_no_neighbour_unchanged(self):
        text = "abc - xyz"
        # raw aggregates: "abc" latin (ws absorbed), "-" symbol (ws absorbed), "xyz" latin
        # Hyphen has WS on both sides → no LATIN-hyphen-LATIN pattern
        spans = _spans(text)
        out = apply_hyphen_bridge_rule(spans, text)
        # No bridge applied; spans unchanged
        assert [s.lang for s in out] == [s.lang for s in spans]

    def test_non_hyphen_symbol_does_not_bridge(self):
        text = "a+b"
        spans = _spans(text)
        out = apply_hyphen_bridge_rule(spans, text)
        # plus is not hyphen → not bridged
        assert [s.lang for s in out] == ["latin", "symbol", "latin"]

    def test_empty(self):
        assert apply_hyphen_bridge_rule([], "") == []


# ---------------------------------------------------------------------------
# T-06 — Number / math unification
# ---------------------------------------------------------------------------


class TestNumUnification:
    def test_decimal_number_unified(self):
        text = "0.05"
        spans = _spans(text)
        # raw: digit, symbol, digit
        out = apply_num_unification(spans, text)
        assert len(out) == 1
        assert out[0].lang == "num"
        assert out[0].start == 0
        assert out[0].end == 4
        assert out[0].confidence == 1.0

    def test_digit_only_becomes_num(self):
        text = "42"
        spans = _spans(text)
        out = apply_num_unification(spans, text)
        assert len(out) == 1
        assert out[0].lang == "num"

    def test_math_expression_unified(self):
        text = "3+5=8"
        spans = _spans(text)
        out = apply_num_unification(spans, text)
        assert len(out) == 1
        assert out[0].lang == "num"

    def test_he_then_digit_keeps_he_separate(self):
        text = "ערך 5"
        spans = _spans(text)
        # raw after aggregate: he (with absorbed ws), digit
        out = apply_num_unification(spans, text)
        assert len(out) == 2
        assert out[0].lang == "he"
        assert out[1].lang == "num"

    def test_standalone_symbol_becomes_num(self):
        text = "%"
        spans = _spans(text)
        out = apply_num_unification(spans, text)
        assert len(out) == 1
        assert out[0].lang == "num"

    def test_empty(self):
        assert apply_num_unification([], "") == []
