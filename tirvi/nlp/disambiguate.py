"""F18 — sense disambiguation.

Wave-1 legacy API: ``_legacy_pick_sense`` (tuple[NLPToken, bool]).
Wave-2 API: ``pick_sense(token: NLPToken) -> NLPToken`` (added T-03).

Spec: N02/F18 DE-03. AC: US-01/AC-01. FT-anchors: FT-127.
BT-anchors: BT-083.
"""

from __future__ import annotations

import os
import warnings

from tirvi.results import NLPToken

from .errors import DisambiguationError
from .overrides import MORPH_HOMOGRAPH_OVERRIDES

_DEFAULT_MARGIN = 0.2
_ENV_VAR = "TIRVI_DISAMBIG_MARGIN"


def pick_sense(
    token: NLPToken,
    candidates: list[tuple[NLPToken, float]] | None = None,
) -> NLPToken:
    """Return the resolved NLPToken for ``token`` using the Wave-2 API.

    • token.ambiguous=False → passthrough (F17 already chose).
    • token.ambiguous=True → probe MORPH_HOMOGRAPH_OVERRIDES keyed by
      (token.text, frozenset((token.morph_features or {}).items())).
    • Override hit → return override.
    • Override miss + candidates supplied → top-1 by score.
    • Override miss + candidates=None → passthrough.
    """
    if not token.ambiguous:
        return token
    key = (token.text, frozenset((token.morph_features or {}).items()))
    override = MORPH_HOMOGRAPH_OVERRIDES.get(key)
    if override is not None:
        return override
    if candidates:
        return max(candidates, key=lambda c: c[1])[0]
    return token


def _legacy_pick_sense(
    candidates: list[tuple[NLPToken, float]],
    margin_threshold: float | None = None,
) -> tuple[NLPToken, bool]:
    """Return ``(top_candidate, ambiguous)`` from a scored candidate list.

    Deprecated: use ``pick_sense(token: NLPToken) -> NLPToken`` instead.
    """
    warnings.warn(
        "_legacy_pick_sense is deprecated; use pick_sense(token, candidates) instead",
        DeprecationWarning,
        stacklevel=2,
    )
    if not candidates:
        raise DisambiguationError("pick_sense requires at least one candidate")
    sorted_cands = sorted(candidates, key=lambda c: c[1], reverse=True)
    top_token, top_score = sorted_cands[0]
    threshold = _resolve_threshold(margin_threshold)
    ambiguous = _is_ambiguous(top_score, sorted_cands, threshold)
    return top_token, ambiguous


def _is_ambiguous(
    top_score: float,
    sorted_cands: list[tuple[NLPToken, float]],
    threshold: float,
) -> bool:
    if len(sorted_cands) < 2:
        return False
    second_score = sorted_cands[1][1]
    return (top_score - second_score) < threshold


def _resolve_threshold(override: float | None) -> float:
    if override is not None:
        return override
    raw = os.environ.get(_ENV_VAR)
    if raw is None:
        return _DEFAULT_MARGIN
    try:
        return float(raw)
    except ValueError:
        return _DEFAULT_MARGIN
