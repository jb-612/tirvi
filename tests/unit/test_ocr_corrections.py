"""Tests for post-OCR Hebrew final-letter correction."""
from unittest.mock import patch
from tirvi.normalize.ocr_corrections import correct_final_letters, _suspicious


class TestSuspicious:
    def test_samech_final(self):
        assert _suspicious("סיוס") is True

    def test_mem_final_not_suspicious(self):
        assert _suspicious("סיום") is False

    def test_empty(self):
        assert _suspicious("") is False


class TestCorrectFinalLetters:
    def test_no_suspicious_words_skips_api(self):
        with patch("tirvi.normalize.ocr_corrections._nakdan_rejects") as m:
            result = correct_final_letters(["שלום", "עולם"])
        m.assert_not_called()
        assert result == ["שלום", "עולם"]

    def test_samech_corrected_to_mem(self):
        # _nakdan_rejects(w) → True for ס-final, False for ם-final
        def rejects(w): return w.endswith("ס")
        with patch("tirvi.normalize.ocr_corrections._nakdan_rejects", side_effect=rejects):
            result = correct_final_letters(["סיוס", "שלום"])
        assert result[0] == "סיום"
        assert result[1] == "שלום"

    def test_valid_samech_not_changed(self):
        def rejects(w): return False  # everything accepted
        with patch("tirvi.normalize.ocr_corrections._nakdan_rejects", side_effect=rejects):
            result = correct_final_letters(["פרס"])
        assert result[0] == "פרס"

    def test_api_error_returns_original(self):
        # Use a word NOT in the hardcoded fix list so it falls through to
        # the API-backed heuristic, where the network error path is exercised.
        def rejects(w): raise Exception("network error")
        with patch("tirvi.normalize.ocr_corrections._nakdan_rejects", side_effect=rejects):
            result = correct_final_letters(["צרורס"])  # not in known fixes
        assert result[0] == "צרורס"

    def test_known_fix_applied_without_api_call(self):
        with patch("tirvi.normalize.ocr_corrections._nakdan_rejects") as m:
            result = correct_final_letters(["גורס"])
        assert result[0] == "גורם"
        m.assert_not_called()
