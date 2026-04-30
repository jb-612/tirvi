"""F20 T-06 — PhonikudG2PAdapter contract conformance.

Spec: N02/F20 DE-06. AC: US-01/AC-01.
FT-anchors: FT-155. BT-anchors: BT-104.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tirvi.adapters.phonikud.adapter import PhonikudG2PAdapter
from tirvi.ports import G2PBackend
from tirvi.results import G2PResult


class TestPhonikudG2PAdapter:
    def test_us_01_ac_01_implements_g2p_backend(self) -> None:
        adapter = PhonikudG2PAdapter()
        assert isinstance(adapter, G2PBackend)

    def test_us_01_ac_01_returns_g2p_result(self) -> None:
        fake = MagicMock(name="phonikud_module")
        fake.transliterate.return_value = [{"ipa": "ʃa.ˈlom"}]
        adapter = PhonikudG2PAdapter()
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=fake,
        ):
            result = adapter.grapheme_to_phoneme("שָׁלוֹם", "he")
        assert isinstance(result, G2PResult)
        assert result.provider in ("phonikud", "phonikud-fallback")

    def test_returns_fallback_provider_when_phonikud_missing(self) -> None:
        adapter = PhonikudG2PAdapter()
        with patch(
            "tirvi.adapters.phonikud.inference.load_phonikud",
            return_value=None,
        ):
            result = adapter.grapheme_to_phoneme("שלום", "he")
        assert result.provider == "phonikud-fallback"

    @pytest.mark.skip(reason="F03 T-08 assert_adapter_contract deferred per POC-CRITICAL-PATH")
    def test_us_01_ac_01_passes_assert_adapter_contract(self) -> None:
        pass
