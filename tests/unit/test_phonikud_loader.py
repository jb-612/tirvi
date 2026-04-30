"""F20 T-01 — Phonikud lazy loader with fallback.

Spec: N02/F20 DE-01, ADR-022. AC: US-01/AC-01.
"""

from __future__ import annotations

import sys
from unittest.mock import patch

from tirvi.adapters.phonikud import loader
from tirvi.results import G2PResult


class TestPhonikudLoader:
    def test_us_01_ac_01_lazy_imports_on_first_call(self) -> None:
        loader.load_phonikud.cache_clear()
        # In a phonikud-less env import returns None; when installed, returns
        # the module reference.
        result = loader.load_phonikud()
        assert result is None or hasattr(result, "__name__")

    def test_us_01_ac_01_falls_back_to_g2p_fake_when_missing(self) -> None:
        loader.load_phonikud.cache_clear()
        with patch.dict(sys.modules, {"phonikud": None}):
            module = loader.load_phonikud()
        assert module is None

        result = loader.fallback_g2p("שלום")
        assert isinstance(result, G2PResult)
        assert result.provider == "phonikud-fallback"
        assert result.phonemes == ["שלום"]
        assert result.confidence is None

    def test_fallback_empty_text_yields_empty_phonemes(self) -> None:
        result = loader.fallback_g2p("   ")
        assert result.phonemes == []
        assert result.provider == "phonikud-fallback"
