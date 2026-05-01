"""F17 T-06 — DictaBERTAdapter adheres to NLPBackend contract + F26 fallback.

Spec: N02/F17 DE-06. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-127. BT-anchors: BT-085.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tirvi.adapters.dictabert.adapter import DictaBERTAdapter
from tirvi.ports import NLPBackend
from tirvi.results import NLPResult, NLPToken


def _patched_pipeline() -> tuple[MagicMock, MagicMock]:
    return MagicMock(), MagicMock()


def _happy_path_patches():
    return (
        patch(
            "tirvi.adapters.dictabert.inference.load_model",
            return_value=_patched_pipeline(),
        ),
        patch(
            "tirvi.adapters.dictabert.inference._run_joint_predict",
            return_value=[NLPToken(text="שלום", pos="NOUN")],
        ),
    )


class TestDictaBERTAdapter:
    def test_us_01_ac_01_implements_nlp_backend_runtime_check(self) -> None:
        adapter = DictaBERTAdapter(model_revision="rev-pinned")
        assert isinstance(adapter, NLPBackend)

    def test_us_01_ac_01_provider_is_dictabert_morph_on_happy_path(self) -> None:
        adapter = DictaBERTAdapter(model_revision="default")
        load_patch, predict_patch = _happy_path_patches()
        with load_patch, predict_patch:
            result = adapter.analyze("שלום", "he")
        assert isinstance(result, NLPResult)
        assert not isinstance(result, bytes)
        assert result.provider == "dictabert-morph"

    def test_us_02_ac_01_falls_back_to_degraded_on_import_error(self) -> None:
        """US-02/AC-01: ImportError from analyze → degraded NLPResult."""
        adapter = DictaBERTAdapter(model_revision="default")
        with patch(
            "tirvi.adapters.dictabert.inference.load_model",
            side_effect=ImportError("transformers not installed"),
        ), patch(
            "tirvi.adapters.dictabert.adapter.importlib.import_module",
            side_effect=ImportError("alephbert not installed"),
        ):
            result = adapter.analyze("שלום", "he")
        assert result.provider == "degraded"
        assert result.tokens == []

    def test_us_02_ac_01_falls_back_to_degraded_on_os_error(self) -> None:
        """US-02/AC-01: OSError (model weights missing) → degraded NLPResult."""
        adapter = DictaBERTAdapter(model_revision="default")
        with patch(
            "tirvi.adapters.dictabert.inference.load_model",
            side_effect=OSError("model weights not found"),
        ), patch(
            "tirvi.adapters.dictabert.adapter.importlib.import_module",
            side_effect=ImportError("alephbert not installed"),
        ):
            result = adapter.analyze("שלום", "he")
        assert result.provider == "degraded"
        assert result.tokens == []

    def test_us_02_ac_01_f26_adapter_instance_is_cached(self) -> None:
        """F26 adapter is instantiated once; second analyze reuses it."""
        adapter = DictaBERTAdapter(model_revision="default")
        fake_f26 = MagicMock()
        fake_f26.analyze.return_value = NLPResult(
            provider="alephbert+yap", tokens=[]
        )
        with patch(
            "tirvi.adapters.dictabert.inference.load_model",
            side_effect=ImportError("transformers not installed"),
        ), patch(
            "tirvi.adapters.dictabert.adapter.importlib.import_module",
        ) as mock_import:
            mock_module = MagicMock()
            mock_module.AlephBertYapFallbackAdapter.return_value = fake_f26
            mock_import.return_value = mock_module
            adapter.analyze("שלום", "he")
            adapter.analyze("עולם", "he")
        assert mock_import.call_count == 1
        assert fake_f26.analyze.call_count == 2

    @pytest.mark.skip(reason="F03 T-08 assert_adapter_contract deferred per POC-CRITICAL-PATH")
    def test_us_01_ac_01_passes_assert_adapter_contract(self) -> None:
        pass
