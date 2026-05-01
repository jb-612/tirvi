"""F20 T-02 — Phonikud whole-text phonemize() invocation (per ADR-028).

Spec: N02/F20 DE-02. AC: US-01/AC-01.
FT-anchors: FT-152, FT-154, FT-157. BT-anchors: BT-101.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tirvi.adapters.phonikud.inference import grapheme_to_phoneme
from tirvi.results import G2PResult


def _fake_phonikud_module(ipa: str) -> MagicMock:
    fake = MagicMock(name="phonikud_module")
    fake.phonemize.return_value = ipa
    return fake


class TestPhonikudInference:
    def test_us_01_ac_01_returns_g2p_result(self) -> None:
        fake = _fake_phonikud_module("ʃa.ˈlom")
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=fake,
        ):
            result = grapheme_to_phoneme("שָׁלוֹם", lang="he")
        assert isinstance(result, G2PResult)
        assert result.provider == "phonikud"

    def test_us_01_ac_01_emits_whole_text_ipa_as_single_element(self) -> None:
        # ADR-028: phonemize returns one IPA string for the whole text;
        # adapter wraps it in a 1-element list to keep the G2PResult shape stable.
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=_fake_phonikud_module("ʃa.ˈlom ˈje.led"),
        ):
            result = grapheme_to_phoneme("שָׁלוֹם יֶלֶד", lang="he")
        assert result.phonemes == ["ʃa.ˈlom ˈje.led"]
        assert len(result.phonemes) == 1

    def test_us_01_ac_01_calls_phonemize_with_predict_vocal_shva_true(self) -> None:
        # ADR-028: vocal-shva prediction is inline via the phonemize keyword.
        fake = _fake_phonikud_module("ʃa.ˈlom")
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=fake,
        ):
            grapheme_to_phoneme("שָׁלוֹם", lang="he")
        fake.phonemize.assert_called_once()
        args, kwargs = fake.phonemize.call_args
        assert args[0] == "שָׁלוֹם"
        assert kwargs.get("predict_vocal_shva") is True

    def test_falls_back_to_identity_when_phonikud_missing(self) -> None:
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=None,
        ):
            result = grapheme_to_phoneme("שלום", lang="he")
        assert result.provider == "phonikud-fallback"
        assert result.phonemes == ["שלום"]

    def test_empty_text_returns_empty_phonemes(self) -> None:
        # T-04: empty / whitespace input short-circuits before calling phonikud.
        result = grapheme_to_phoneme("   ", lang="he")
        assert result.phonemes == []

    def test_us_01_ac_01_ft_154_returns_non_empty_phonemes_for_vowel_bearing_input(
        self,
    ) -> None:
        # T-03: vocal-shva is inline via phonemize(predict_vocal_shva=True);
        # smoke assertion only — precise vowel content not pinned in POC.
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=_fake_phonikud_module("ʃa.ˈlom"),
        ):
            result = grapheme_to_phoneme("שָׁלוֹם", lang="he")
        assert len(result.phonemes) > 0
        assert result.phonemes[0]
