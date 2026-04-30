"""F17 T-01 — DictaBERT module-level LRU loader.

Spec: N02/F17 DE-01, ADR-020. AC: US-01/AC-01. FT-anchors: FT-125.
BT-anchors: BT-086.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# Stub transformers before importing so the deferred import inside load_model()
# resolves without the real package present (ADR-014 vendor boundary).
# Read back from sys.modules so multiple test files share one stub object.
if "transformers" not in sys.modules:
    sys.modules["transformers"] = MagicMock()
_stub_transformers = sys.modules["transformers"]

from tirvi.adapters.dictabert import loader  # noqa: E402


class TestDictaBERTLoader:
    def setup_method(self, _method: object) -> None:
        loader.load_model.cache_clear()
        _stub_transformers.AutoModelForTokenClassification.from_pretrained.reset_mock()
        _stub_transformers.AutoTokenizer.from_pretrained.reset_mock()

    def test_us_01_ac_01_loader_is_lru_cached(self) -> None:
        sentinel_model = MagicMock(name="model")
        sentinel_tokenizer = MagicMock(name="tokenizer")
        _stub_transformers.AutoModelForTokenClassification.from_pretrained.return_value = sentinel_model
        _stub_transformers.AutoTokenizer.from_pretrained.return_value = sentinel_tokenizer

        first = loader.load_model()
        second = loader.load_model()

        assert first is second
        assert _stub_transformers.AutoModelForTokenClassification.from_pretrained.call_count == 1
        assert _stub_transformers.AutoTokenizer.from_pretrained.call_count == 1

    def test_us_01_ac_01_loader_lazy_first_call(self) -> None:
        _stub_transformers.AutoModelForTokenClassification.from_pretrained.assert_not_called()
        loader.load_model()
        assert _stub_transformers.AutoModelForTokenClassification.from_pretrained.call_count == 1
