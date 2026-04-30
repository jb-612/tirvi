"""F20 T-02 — Phonikud per-token transliteration.

Spec: N02/F20 DE-02. AC: US-01/AC-01.
FT-anchors: FT-152, FT-154, FT-157. BT-anchors: BT-101.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tirvi.adapters.phonikud.inference import grapheme_to_phoneme
from tirvi.results import G2PResult


def _fake_phonikud_module(per_token_output: list[dict[str, object]]) -> MagicMock:
    fake = MagicMock(name="phonikud_module")
    fake.transliterate.return_value = per_token_output
    return fake


class TestPhonikudInference:
    def test_us_01_ac_01_returns_g2p_result(self) -> None:
        fake = _fake_phonikud_module(
            [{"ipa": "ʃa.ˈlom", "stress": 2}]
        )
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=fake,
        ):
            result = grapheme_to_phoneme("שָׁלוֹם", lang="he")
        assert isinstance(result, G2PResult)
        assert result.provider == "phonikud"

    def test_us_01_ac_01_emits_ipa_per_token(self) -> None:
        per_token = [
            {"ipa": "ʃa.ˈlom", "stress": 2},
            {"ipa": "ˈje.led", "stress": 1},
        ]
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=_fake_phonikud_module(per_token),
        ):
            result = grapheme_to_phoneme("שָׁלוֹם יֶלֶד", lang="he")
        assert result.phonemes == ["ʃa.ˈlom", "ˈje.led"]

    def test_us_01_ac_01_preserves_phonikud_1_based_stress(self) -> None:
        # Phonikud emits 1-based stress index. Adapter forwards unchanged.
        per_token = [{"ipa": "ʃa.ˈlom", "stress": 2}]
        fake = _fake_phonikud_module(per_token)
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=fake,
        ):
            grapheme_to_phoneme("שָׁלוֹם", lang="he")
        # transliterate was invoked exactly once with the input text
        fake.transliterate.assert_called_once()

    def test_falls_back_to_identity_when_phonikud_missing(self) -> None:
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=None,
        ):
            result = grapheme_to_phoneme("שלום", lang="he")
        assert result.provider == "phonikud-fallback"
        assert result.phonemes == ["שלום"]

    def test_empty_text_returns_empty_phonemes(self) -> None:
        result = grapheme_to_phoneme("   ", lang="he")
        assert result.phonemes == []
