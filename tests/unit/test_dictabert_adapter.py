"""F17 T-06 — DictaBERTAdapter adheres to NLPBackend contract.

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


class TestDictaBERTAdapter:
    def test_us_01_ac_01_implements_nlp_backend_runtime_check(self) -> None:
        adapter = DictaBERTAdapter(model_revision="rev-pinned")
        assert isinstance(adapter, NLPBackend)

    def test_us_01_ac_01_returns_nlp_result_never_bytes(self) -> None:
        adapter = DictaBERTAdapter(model_revision="default")
        with patch(
            "tirvi.adapters.dictabert.inference.load_model",
            return_value=_patched_pipeline(),
        ), patch(
            "tirvi.adapters.dictabert.inference._run_joint_predict",
            return_value=[NLPToken(text="שלום", pos="NOUN")],
        ):
            result = adapter.analyze("שלום", "he")
        assert isinstance(result, NLPResult)
        assert not isinstance(result, bytes)
        assert result.provider == "dictabert-large-joint"

    @pytest.mark.skip(reason="F03 T-08 assert_adapter_contract deferred per POC-CRITICAL-PATH")
    def test_us_01_ac_01_passes_assert_adapter_contract(self) -> None:
        pass
