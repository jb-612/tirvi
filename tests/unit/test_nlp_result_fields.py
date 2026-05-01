"""F18 T-03 — NLPResult field shape (POC numbering).

Spec: N02/F18 DE-01. AC: US-01/AC-01. FT-anchors: FT-136, FT-137.
"""

from __future__ import annotations

import dataclasses

from tirvi.results import NLPResult, NLPToken


class TestNLPResultFields:
    def test_us_01_ac_01_provider_field_required(self) -> None:
        result = NLPResult(provider="dictabert-large-joint", tokens=[])
        assert result.provider == "dictabert-large-joint"
        # No default for provider — it must be supplied.
        provider_field = next(
            f for f in dataclasses.fields(NLPResult) if f.name == "provider"
        )
        assert provider_field.default is dataclasses.MISSING

    def test_us_01_ac_01_tokens_list_required(self) -> None:
        result = NLPResult(provider="x", tokens=[NLPToken(text="hi")])
        assert isinstance(result.tokens, list)
        assert len(result.tokens) == 1

    def test_us_01_ac_01_token_carries_confidence(self) -> None:
        token = NLPToken(text="ילד", pos="NOUN", confidence=0.91)
        assert token.confidence == 0.91

    def test_token_confidence_defaults_none_not_zero(self) -> None:
        token = NLPToken(text="ילד", pos="NOUN")
        assert token.confidence is None

    def test_token_carries_morph_and_ambiguous(self) -> None:
        morph = {"Gender": "Masc", "Number": "Sing"}
        token = NLPToken(
            text="ספר",
            pos="NOUN",
            morph_features=morph,
            ambiguous=True,
        )
        assert token.morph_features == morph
        assert token.ambiguous is True
