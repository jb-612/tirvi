"""F19 T-01 — Nakdan model loader.

Spec: N02/F19 DE-01, ADR-021. AC: US-01/AC-01. BT-anchors: BT-099.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tirvi.adapters.nakdan import loader


class TestNakdanLoader:
    def test_us_01_ac_01_loader_is_lru_cached(self) -> None:
        loader.load_model.cache_clear()
        sentinel_model = MagicMock(name="model")
        sentinel_tokenizer = MagicMock(name="tokenizer")
        with patch.object(
            loader.AutoModelForSeq2SeqLM,
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

    def test_us_01_ac_01_releases_cuda_cache_between_stages(self) -> None:
        with patch.object(
            loader.torch.cuda, "is_available", return_value=True
        ), patch.object(loader.torch.cuda, "empty_cache") as empty_mock:
            loader.release_cache()
        empty_mock.assert_called_once()

    def test_release_cache_is_no_op_when_cuda_unavailable(self) -> None:
        with patch.object(
            loader.torch.cuda, "is_available", return_value=False
        ), patch.object(loader.torch.cuda, "empty_cache") as empty_mock:
            loader.release_cache()
        empty_mock.assert_not_called()
