"""T-02 — Unicode-script per-character classifier (F16 DE-01)."""

import pytest

from tirvi.lang_spans.classify import Script, classify_char


class TestClassifyChar:
    @pytest.mark.parametrize("c", ["א", "ב", "ת", "ש", "א", "ת"])
    def test_hebrew_base_block(self, c):
        assert classify_char(c) is Script.HE

    @pytest.mark.parametrize("c", ["יִ", "שׁ", "ﭏ"])
    def test_hebrew_presentation_forms(self, c):
        assert classify_char(c) is Script.HE

    @pytest.mark.parametrize("c", ["a", "Z", "m", "P", "ñ", "É"])
    def test_latin(self, c):
        assert classify_char(c) is Script.LATIN

    @pytest.mark.parametrize("c", ["0", "5", "9"])
    def test_ascii_digits(self, c):
        assert classify_char(c) is Script.DIGIT

    @pytest.mark.parametrize("c", ["٠", "٥", "٩"])
    def test_arabic_indic_digits(self, c):
        assert classify_char(c) is Script.DIGIT

    @pytest.mark.parametrize("c", ["+", "−", "×", "÷", "=", "%", ".", ","])
    def test_math_and_decimal_symbols(self, c):
        assert classify_char(c) is Script.SYMBOL

    @pytest.mark.parametrize("c", [" ", "\t", "\n"])
    def test_whitespace(self, c):
        assert classify_char(c) is Script.WS

    @pytest.mark.parametrize("c", ["@", "中", "❀", "؟"])
    def test_other(self, c):
        assert classify_char(c) is Script.OTHER

    def test_hyphen_is_symbol(self):
        assert classify_char("-") is Script.SYMBOL
