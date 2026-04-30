"""F17 T-01 — DictaBERT module-level LRU loader.

Spec: N02/F17 DE-01, ADR-020. AC: US-01/AC-01. FT-anchors: FT-125.
BT-anchors: BT-086.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tirvi.adapters.dictabert import loader


class TestDictaBERTLoader:
    def test_us_01_ac_01_loader_is_lru_cached(self) -> None:
        loader.load_model.cache_clear()
        sentinel_model = MagicMock(name="model")
        sentinel_tokenizer = MagicMock(name="tokenizer")
        with patch.object(
            loader.AutoModelForTokenClassification,
            "from_pretrained",
            return_value=sentinel_model,
        ) as model_mock, patch.object(
            loader.AutoTokenizer,
            "from_pretrained",
            return_value=sentinel_tokenizer,
        ) as tok_mock:
            first = loader.load_model()
            second = loader.load_model()
        assert first is second
        assert model_mock.call_count == 1
        assert tok_mock.call_count == 1

    def test_us_01_ac_01_loader_lazy_first_call(self) -> None:
        loader.load_model.cache_clear()
        with patch.object(
            loader.AutoModelForTokenClassification,
            "from_pretrained",
        ) as model_mock, patch.object(loader.AutoTokenizer, "from_pretrained"):
            model_mock.assert_not_called()
            loader.load_model()
            assert model_mock.call_count == 1
