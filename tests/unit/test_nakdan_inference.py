"""F19 T-03 — Nakdan seq2seq inference.

Spec: N02/F19 DE-03. AC: US-01/AC-01. FT-anchors: FT-150.
"""

from __future__ import annotations

import unicodedata
from unittest.mock import MagicMock, patch

from tirvi.adapters.nakdan.inference import PROVIDER, diacritize
from tirvi.results import DiacritizationResult


def _patched(diacritized: str, confidence: float | None) -> tuple:
    return MagicMock(), MagicMock(), {
        "diacritized": diacritized,
        "confidence": confidence,
    }


class TestNakdanInference:
    def test_us_01_ac_01_returns_diacritization_result(self) -> None:
        with patch(
            "tirvi.adapters.nakdan.inference.load_model",
            return_value=(MagicMock(), MagicMock()),
        ), patch(
            "tirvi.adapters.nakdan.inference._run_diacritization",
            return_value={"diacritized": "שָׁלוֹם", "confidence": 0.85},
        ):
            result = diacritize("שלום")
        assert isinstance(result, DiacritizationResult)
        assert result.provider == PROVIDER

    def test_us_01_ac_01_per_token_softmax_margin_in_confidence(self) -> None:
        with patch(
            "tirvi.adapters.nakdan.inference.load_model",
            return_value=(MagicMock(), MagicMock()),
        ), patch(
            "tirvi.adapters.nakdan.inference._run_diacritization",
            return_value={"diacritized": "שָׁלוֹם", "confidence": 0.72},
        ):
            result = diacritize("שלום")
        assert result.confidence == 0.72

    def test_diacritized_text_is_nfd(self) -> None:
        # Ensure the returned text is in NFD form (per F19 T-05).
        nfc_result = unicodedata.normalize("NFC", "שָׁלוֹם")
        with patch(
            "tirvi.adapters.nakdan.inference.load_model",
            return_value=(MagicMock(), MagicMock()),
        ), patch(
            "tirvi.adapters.nakdan.inference._run_diacritization",
            return_value={"diacritized": nfc_result, "confidence": 0.9},
        ):
            result = diacritize("שלום")
        assert unicodedata.is_normalized("NFD", result.diacritized_text)

    def test_empty_input_skips_model(self) -> None:
        with patch(
            "tirvi.adapters.nakdan.inference.load_model"
        ) as mock_load:
            result = diacritize("   ")
        assert result.diacritized_text == ""
        assert result.confidence is None
        mock_load.assert_not_called()
