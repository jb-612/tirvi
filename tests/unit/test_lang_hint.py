"""F08 T-04 — Inline lang_hint detector.

Spec: N01/F08 DE-04. AC: US-01/AC-01. FT-anchors: FT-058.
"""

from __future__ import annotations

from tirvi.adapters.tesseract.lang_hint import detect_lang_hint


class TestLangHintDetector:
    def test_us_01_ac_01_ft_058_marks_hebrew_words_he(self) -> None:
        assert detect_lang_hint("שלום") == "he"

    def test_us_01_ac_01_ft_058_marks_english_words_en(self) -> None:
        assert detect_lang_hint("Hello") == "en"

    def test_us_01_ac_01_ft_058_unknown_script_returns_none(self) -> None:
        assert detect_lang_hint("123") is None
        assert detect_lang_hint("...") is None
        assert detect_lang_hint("") is None

    def test_mixed_script_with_hebrew_returns_he(self) -> None:
        assert detect_lang_hint("שלוםabc") == "he"

    def test_english_with_digits_returns_en(self) -> None:
        assert detect_lang_hint("abc123") == "en"
