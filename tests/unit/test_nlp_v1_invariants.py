"""F18 T-05 — assert_nlp_result_v1 contract harness.

Spec: N02/F18 DE-05, DE-06. AC: US-01/AC-01, AC-04, AC-05, AC-06.
FT-anchors: FT-139, FT-140. BT-anchors: BT-091, BT-093.
"""

from __future__ import annotations

import pytest

from tirvi.errors import SchemaContractError
from tirvi.nlp.contracts import assert_nlp_result_v1
from tirvi.results import NLPResult, NLPToken


def _token(**kwargs) -> NLPToken:
    defaults = {"text": "ילד", "pos": "NOUN"}
    return NLPToken(**{**defaults, **kwargs})


class TestNLPv1Invariants:
    def test_provider_dictabert_morph_accepted(self) -> None:
        result = NLPResult(provider="dictabert-morph", tokens=[_token()])
        assert_nlp_result_v1(result)

    def test_provider_alephbert_plus_yap_accepted(self) -> None:
        """AC-06: alephbert+yap (plus sign) is a valid provider."""
        result = NLPResult(provider="alephbert+yap", tokens=[_token()])
        assert_nlp_result_v1(result)

    def test_provider_alephbert_dash_yap_accepted_transitional(self) -> None:
        """AC-06: alephbert-yap (dash form) is accepted as transitional alias."""
        result = NLPResult(provider="alephbert-yap", tokens=[_token()])
        assert_nlp_result_v1(result)

    def test_provider_degraded_with_empty_tokens_accepted(self) -> None:
        """AC-04: degraded provider with empty token list is valid."""
        result = NLPResult(provider="degraded", tokens=[])
        assert_nlp_result_v1(result)

    def test_provider_degraded_with_nonempty_tokens_rejected(self) -> None:
        result = NLPResult(provider="degraded", tokens=[_token()])
        with pytest.raises(SchemaContractError):
            assert_nlp_result_v1(result)

    def test_provider_legacy_dictabert_large_joint_rejected_with_substring(self) -> None:
        """AC-05: legacy provider raises SchemaContractError with ADR-026 reference."""
        result = NLPResult(provider="dictabert-large-joint", tokens=[])
        with pytest.raises(SchemaContractError) as exc_info:
            assert_nlp_result_v1(result)
        msg = str(exc_info.value)
        assert "legacy provider" in msg
        assert "ADR-026" in msg

    def test_provider_unknown_rejected(self) -> None:
        result = NLPResult(provider="unknown-model", tokens=[])
        with pytest.raises(SchemaContractError):
            assert_nlp_result_v1(result)

    def test_morph_keys_titlecase_accepted(self) -> None:
        token = _token(morph_features={"Gender": "Masc", "Number": "Sing"})
        result = NLPResult(provider="dictabert-morph", tokens=[token])
        assert_nlp_result_v1(result)

    def test_morph_keys_lowercase_rejected(self) -> None:
        """R-3 regression: lowercase morph keys must be rejected."""
        token = _token(morph_features={"gender": "Masc"})
        result = NLPResult(provider="dictabert-morph", tokens=[token])
        with pytest.raises(SchemaContractError):
            assert_nlp_result_v1(result)

    def test_confidence_out_of_range_rejected(self) -> None:
        token = _token(confidence=1.5)
        result = NLPResult(provider="dictabert-morph", tokens=[token])
        with pytest.raises(SchemaContractError):
            assert_nlp_result_v1(result)

    def test_lemma_none_accepted(self) -> None:
        token = _token(lemma=None)
        result = NLPResult(provider="dictabert-morph", tokens=[token])
        assert_nlp_result_v1(result)

    def test_pos_not_in_whitelist_rejected(self) -> None:
        token = _token(pos="BLAH")
        result = NLPResult(provider="dictabert-morph", tokens=[token])
        with pytest.raises(SchemaContractError):
            assert_nlp_result_v1(result)
