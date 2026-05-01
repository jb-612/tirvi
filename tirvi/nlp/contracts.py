"""F18 T-05 — NLPResult v1 contract assertion.

Spec: N02/F18 DE-05, DE-06. AC: US-01/AC-01, AC-04, AC-05, AC-06.
FT-anchors: FT-139, FT-140. BT-anchors: BT-091, BT-093.
"""

from __future__ import annotations

from tirvi.errors import SchemaContractError
from tirvi.results import NLPResult, NLPToken

from .morph import MORPH_KEYS_WHITELIST

ALLOWED_PROVIDERS: frozenset[str] = frozenset({
    "dictabert-morph",
    "alephbert+yap",
    "alephbert-yap",
    "fixture",
    "degraded",
})

UD_POS_WHITELIST: frozenset[str] = frozenset({
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ",
    "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT",
    "SCONJ", "SYM", "VERB", "X",
})


def assert_nlp_result_v1(result: NLPResult) -> None:
    """Assert that ``result`` conforms to the F18 NLPResult v1 contract.

    Raises :class:`tirvi.errors.SchemaContractError` on any violation.
    """
    _assert_provider(result.provider)
    if result.provider == "degraded":
        _assert_degraded(result)
        return
    for token in result.tokens:
        _assert_token(token)


def _assert_provider(provider: str) -> None:
    if provider == "dictabert-large-joint":
        raise SchemaContractError(
            f"legacy provider '{provider}' is no longer accepted — see ADR-026"
        )
    if provider not in ALLOWED_PROVIDERS:
        raise SchemaContractError(
            f"unknown provider '{provider}'; allowed: {sorted(ALLOWED_PROVIDERS)}"
        )


def _assert_degraded(result: NLPResult) -> None:
    if result.tokens:
        raise SchemaContractError("degraded result must have empty tokens")


def _assert_token(token: NLPToken) -> None:
    _assert_pos(token.pos)
    _assert_morph(token.morph_features)
    _assert_confidence(token.confidence)


def _assert_pos(pos: str | None) -> None:
    if pos is None:
        return
    if pos not in UD_POS_WHITELIST:
        raise SchemaContractError(f"token pos '{pos}' not in UD POS whitelist")


def _assert_morph(morph_features: dict[str, str] | None) -> None:
    if morph_features is None:
        return
    unknown = set(morph_features) - MORPH_KEYS_WHITELIST
    if unknown:
        raise SchemaContractError(
            f"morph_features keys not in UD TitleCase whitelist: {sorted(unknown)}"
        )


def _assert_confidence(confidence: float | None) -> None:
    if confidence is None:
        return
    if not (0.0 <= confidence <= 1.0):
        raise SchemaContractError(
            f"token confidence {confidence!r} out of range [0.0, 1.0]"
        )
