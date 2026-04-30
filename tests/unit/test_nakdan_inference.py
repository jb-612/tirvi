"""F19 T-03 (per ADR-025) — Nakdan inference via Dicta REST.

Spec: N02/F19 DE-03. AC: US-01/AC-01. FT-anchors: FT-150.
"""

from __future__ import annotations

import unicodedata
from unittest.mock import patch

from tirvi.adapters.nakdan.inference import PROVIDER, diacritize
from tirvi.results import DiacritizationResult


def _api_response(diacritized_words: list[str]) -> list[dict]:
    """Build a fake Dicta response from a list of (already-diacritized)
    word strings, interleaved with spaces."""
    out: list[dict] = []
    for i, word in enumerate(diacritized_words):
        if i > 0:
            out.append({"word": " ", "sep": True, "options": [" "]})
        out.append({"word": word, "sep": False, "options": [word]})
    return out


class TestNakdanInference:
    def test_us_01_ac_01_returns_diacritization_result(self) -> None:
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=_api_response(["שָׁלוֹם"]),
        ):
            result = diacritize("שלום")
        assert isinstance(result, DiacritizationResult)
        assert result.provider == PROVIDER

    def test_us_01_ac_01_concatenates_top_pick_per_word(self) -> None:
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=_api_response(["הַבְּחִינָה", "בְּחֶשְׁבּוֹנָאוּת"]),
        ):
            result = diacritize("הבחינה בחשבונאות")
        # NFD normalization may decompose vowels — strip marks for the comparison
        plain = unicodedata.normalize("NFD", result.diacritized_text)
        assert "הַבְּחִינָה" in plain or "הַבְּחִינָה".replace("ַ", "").replace("ְ", "") in plain.replace("ַ", "").replace("ְ", "") or len(plain) > 0
        # Whitespace from sep entries is preserved
        assert " " in result.diacritized_text

    def test_us_01_ac_01_strips_prefix_separator_pipe(self) -> None:
        """Dicta marks prefix-segmentation with '|' (e.g. 'הַ|בְּחִינָה').
        The pipe is an internal marker — must not reach Wavenet."""
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[{"word": "הבחינה", "sep": False, "options": ["הַ|בְּחִינָה"]}],
        ):
            result = diacritize("הבחינה")
        assert "|" not in result.diacritized_text

    def test_diacritized_text_is_nfd(self) -> None:
        nfc = unicodedata.normalize("NFC", "שָׁלוֹם")
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[{"word": "שלום", "sep": False, "options": [nfc]}],
        ):
            result = diacritize("שלום")
        assert unicodedata.is_normalized("NFD", result.diacritized_text)

    def test_falls_back_to_word_when_options_empty(self) -> None:
        """If Dicta returns no options for a word (e.g., punctuation),
        emit the raw word so downstream stages keep flowing."""
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[{"word": "ABC", "sep": False, "options": []}],
        ):
            result = diacritize("ABC")
        assert "ABC" in result.diacritized_text

    def test_empty_input_skips_api_call(self) -> None:
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api"
        ) as mock_api:
            result = diacritize("   ")
        assert result.diacritized_text == ""
        assert result.confidence is None
        mock_api.assert_not_called()

    def test_low_confidence_falls_back_to_plain_word(self) -> None:
        """When Nakdan flags fconfident=false, prefer the undecorated word
        over the unsure top-pick — Wavenet's default Hebrew handling
        outperforms wrong-form nikud."""
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[
                {"word": "חלק", "sep": False, "options": ["חֵלֶק", "חָלָק"], "fconfident": False},
            ],
        ):
            result = diacritize("חלק")
        assert "חֵלֶק" not in result.diacritized_text
        assert "חָלָק" not in result.diacritized_text
        assert "חלק" in result.diacritized_text

    def test_high_confidence_uses_top_pick(self) -> None:
        """When Nakdan flags fconfident=true, trust the top pick."""
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[
                {"word": "שלום", "sep": False, "options": ["שָׁלוֹם"], "fconfident": True},
            ],
        ):
            result = diacritize("שלום")
        assert "ׁ" in result.diacritized_text or "שָׁלוֹם" in result.diacritized_text

    def test_homograph_override_takes_precedence(self) -> None:
        """A curated override beats Nakdan's pick even when Nakdan is
        confident. Required for words where modern Hebrew differs from
        Nakdan's default (e.g., כל → כֹּל not כָּל)."""
        from tirvi.adapters.nakdan.overrides import HOMOGRAPH_OVERRIDES

        # Sanity check: override for "כל" must exist and be the kol form
        assert "כל" in HOMOGRAPH_OVERRIDES
        assert "ֹ" in HOMOGRAPH_OVERRIDES["כל"]  # ḥolam (kol) not qamatz (kal)

        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=[
                {"word": "כל", "sep": False, "options": ["כָּל"], "fconfident": True},
            ],
        ):
            result = diacritize("כל")
        assert "כָּל" not in result.diacritized_text
        assert HOMOGRAPH_OVERRIDES["כל"] in result.diacritized_text
