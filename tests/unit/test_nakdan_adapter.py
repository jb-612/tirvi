"""F19 T-06 — DictaNakdanAdapter contract conformance.

Spec: N02/F19 DE-06. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-148, FT-151. BT-anchors: BT-100.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tirvi.adapters.nakdan.adapter import DictaNakdanAdapter
from tirvi.ports import DiacritizerBackend
from tirvi.results import DiacritizationResult


class TestDictaNakdanAdapter:
    def test_us_01_ac_01_implements_diacritizer_backend(self) -> None:
        adapter = DictaNakdanAdapter()
        assert isinstance(adapter, DiacritizerBackend)

    def test_us_01_ac_01_returns_diacritization_result(self) -> None:
        # Per ADR-025 the adapter delegates to the Dicta REST client, not
        # the in-process loader. Mock the API at the inference seam.
        adapter = DictaNakdanAdapter()
        canned = [{"word": "שלום", "sep": False, "options": ["שָׁלוֹם"]}]
        with patch(
            "tirvi.adapters.nakdan.inference.diacritize_via_api",
            return_value=canned,
        ):
            result = adapter.diacritize("שלום")
        assert isinstance(result, DiacritizationResult)
        assert result.provider == "dicta-nakdan-rest"

    @pytest.mark.skip(reason="F03 T-08 assert_adapter_contract deferred per POC-CRITICAL-PATH")
    def test_us_01_ac_01_passes_assert_adapter_contract(self) -> None:
        pass
