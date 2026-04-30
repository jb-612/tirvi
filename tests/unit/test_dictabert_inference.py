"""F17 T-02 — DictaBERT inference + UD-Hebrew label mapping.

Spec: N02/F17 DE-02. AC: US-01/AC-01. FT-anchors: FT-124, FT-130.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator
from unittest.mock import MagicMock, patch

from tirvi.adapters.dictabert.inference import PROVIDER, analyze
from tirvi.results import NLPResult, NLPToken

UD_HEBREW_TAGS = {
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM",
    "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X",
}


@contextmanager
def _patched_pipeline(canned: list[NLPToken]) -> Iterator[None]:
    fake_model = MagicMock(name="model")
    fake_tokenizer = MagicMock(name="tokenizer")
    with patch(
        "tirvi.adapters.dictabert.inference.load_model",
        return_value=(fake_model, fake_tokenizer),
    ), patch(
        "tirvi.adapters.dictabert.inference._run_joint_predict",
        return_value=canned,
    ):
        yield


class TestDictaBERTInference:
    def test_us_01_ac_01_returns_nlp_result(self) -> None:
        with _patched_pipeline([NLPToken(text="שלום", pos="NOUN")]):
            result = analyze("שלום", lang="he")
        assert isinstance(result, NLPResult)
        assert result.provider == PROVIDER
        assert len(result.tokens) == 1

    def test_us_01_ac_01_pos_tags_in_ud_hebrew_set(self) -> None:
        canned = [
            NLPToken(text="ילד", pos="NOUN"),
            NLPToken(text="רץ", pos="VERB"),
        ]
        with _patched_pipeline(canned):
            result = analyze("ילד רץ", lang="he")
        for token in result.tokens:
            assert token.pos in UD_HEBREW_TAGS

    def test_us_01_ac_01_pinned_model_revision(self) -> None:
        fake_model = MagicMock()
        fake_tokenizer = MagicMock()
        with patch(
            "tirvi.adapters.dictabert.inference.load_model",
            return_value=(fake_model, fake_tokenizer),
        ) as mock_load, patch(
            "tirvi.adapters.dictabert.inference._run_joint_predict",
            return_value=[],
        ):
            analyze("שלום", lang="he", revision="rev-2026-pinned")
        mock_load.assert_called_once_with("rev-2026-pinned")

    def test_empty_text_returns_empty_tokens_no_model_load(self) -> None:
        with patch(
            "tirvi.adapters.dictabert.inference.load_model"
        ) as mock_load:
            result = analyze("   ", lang="he")
        assert result.tokens == []
        mock_load.assert_not_called()
