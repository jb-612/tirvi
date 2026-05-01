"""Tests for kamatz-katan post-Nakdan normalization."""
from tirvi.normalize.kamatz_katan import fix_kamatz_katan


class TestKamatzKatan:
    def test_kol_kamatz_to_cholam(self):
        assert fix_kamatz_katan("כָּל") == "כֹּל"

    def test_be_khol_compound(self):
        assert fix_kamatz_katan("בְּכָל שלב") == "בְּכֹל שלב"

    def test_le_khol_compound(self):
        assert fix_kamatz_katan("לְכָל שאלה") == "לְכֹל שאלה"

    def test_chochma(self):
        assert fix_kamatz_katan("חָכְמָה") == "חוֹכְמָה"

    def test_no_kamatz_katan_unchanged(self):
        assert fix_kamatz_katan("שָׁלוֹם") == "שָׁלוֹם"

    def test_empty_unchanged(self):
        assert fix_kamatz_katan("") == ""
