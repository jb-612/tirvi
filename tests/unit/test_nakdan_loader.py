"""F19 T-01 — Nakdan model loader.

Spec: N02/F19 DE-01, ADR-021. AC: US-01/AC-01. BT-anchors: BT-099.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# Stub vendor packages so deferred imports inside load_model() / release_cache()
# resolve without the real packages present (ADR-014 vendor boundary).
# Read back from sys.modules so multiple test files share one stub object.
if "transformers" not in sys.modules:
    sys.modules["transformers"] = MagicMock()
if "torch" not in sys.modules:
    sys.modules["torch"] = MagicMock()
_stub_transformers = sys.modules["transformers"]
_stub_torch = sys.modules["torch"]

from tirvi.adapters.nakdan import loader  # noqa: E402


class TestNakdanLoader:
    def setup_method(self, _method: object) -> None:
        loader.load_model.cache_clear()
        _stub_transformers.AutoModelForSeq2SeqLM.from_pretrained.reset_mock()
        _stub_transformers.AutoTokenizer.from_pretrained.reset_mock()
        _stub_torch.cuda.is_available.reset_mock()
        _stub_torch.cuda.empty_cache.reset_mock()

    def test_us_01_ac_01_loader_is_lru_cached(self) -> None:
        sentinel_model = MagicMock(name="model")
        sentinel_tokenizer = MagicMock(name="tokenizer")
        _stub_transformers.AutoModelForSeq2SeqLM.from_pretrained.return_value = sentinel_model
        _stub_transformers.AutoTokenizer.from_pretrained.return_value = sentinel_tokenizer

        first = loader.load_model()
        second = loader.load_model()

        assert first is second
        assert _stub_transformers.AutoModelForSeq2SeqLM.from_pretrained.call_count == 1
        assert _stub_transformers.AutoTokenizer.from_pretrained.call_count == 1

    def test_us_01_ac_01_releases_cuda_cache_between_stages(self) -> None:
        _stub_torch.cuda.is_available.return_value = True
        loader.release_cache()
        _stub_torch.cuda.empty_cache.assert_called_once()

    def test_release_cache_is_no_op_when_cuda_unavailable(self) -> None:
        _stub_torch.cuda.is_available.return_value = False
        loader.release_cache()
        _stub_torch.cuda.empty_cache.assert_not_called()
