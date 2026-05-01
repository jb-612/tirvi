"""Tests for OCR artefact stripping."""
from tirvi.normalize.ocr_artifacts import (
    strip_slash_suffix,
    strip_wrap_chars,
    clean_ocr_artifacts,
)


class TestStripSlashSuffix:
    def test_lanivhan_t(self):
        assert strip_slash_suffix("לנבחן/ת") == "לנבחן"

    def test_student_iyot(self):
        assert strip_slash_suffix("סטודנט/ית") == "סטודנט"

    def test_ot(self):
        assert strip_slash_suffix("מורה/ות") == "מורה"

    def test_long_suffix_preserved(self):
        # ו/או is "and/or" — common Hebrew expression, not gender slash
        assert strip_slash_suffix("ו/או") == "ו/או"

    def test_no_slash_unchanged(self):
        assert strip_slash_suffix("שלום") == "שלום"


class TestStripWrapChars:
    def test_double_apostrophe_wrap(self):
        assert strip_wrap_chars("''סגורות''") == "סגורות"

    def test_paren_quote_wrap_with_period(self):
        assert strip_wrap_chars("(''סגורות'').") == "סגורות."

    def test_no_wrap_unchanged(self):
        assert strip_wrap_chars("שלום") == "שלום"

    def test_only_punctuation_preserved(self):
        assert strip_wrap_chars("שלום.") == "שלום."


class TestCleanOcrArtifacts:
    def test_combined_pipeline(self):
        result = clean_ocr_artifacts(
            ["לנבחן/ת", "שלום", "(''סגורות'').", "ו/או"]
        )
        assert result == ["לנבחן", "שלום", "סגורות.", "ו/או"]
