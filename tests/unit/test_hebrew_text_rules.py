"""Tests for Hebrew text normalization rules."""
from tirvi.normalize.hebrew_text_rules import (
    expand_geresh_ordinal,
    expand_gender_slash,
    apply_hebrew_text_rules,
)


class TestGereshOrdinal:
    def test_aleph(self):
        assert expand_geresh_ordinal("חלק א׳") == "חלק אלף"

    def test_bet(self):
        assert expand_geresh_ordinal("חלק ב׳") == "חלק בית"

    def test_gimel(self):
        assert expand_geresh_ordinal("חלק ג׳") == "חלק גימל"

    def test_multiple(self):
        assert expand_geresh_ordinal("א׳ ב׳ ג׳") == "אלף בית גימל"

    def test_no_geresh_unchanged(self):
        assert expand_geresh_ordinal("חלק א") == "חלק א"

    def test_regular_apostrophe_ignored(self):
        # U+0027 apostrophe is NOT a geresh
        assert expand_geresh_ordinal("it's") == "it's"


class TestGenderSlash:
    def test_lanivhan_t(self):
        result = expand_gender_slash("לנבחן/ת")
        assert result == "לנבחן, נבחנת"

    def test_student_iyot(self):
        result = expand_gender_slash("סטודנט/ית")
        assert result == "סטודנט, סטודנטית"

    def test_no_slash_unchanged(self):
        assert expand_gender_slash("שלום") == "שלום"

    def test_math_slash_ignored(self):
        # Non-Hebrew characters around slash → not a gender slash
        assert expand_gender_slash("1/2") == "1/2"


class TestApplyAll:
    def test_exam_header(self):
        result = apply_hebrew_text_rules("לנבחן/ת שלום! הנחיות לחלק א׳")
        assert "לנבחן, נבחנת" in result
        assert "אלף" in result
        assert "שלום!" in result
