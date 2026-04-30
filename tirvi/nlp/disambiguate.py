"""F18 T-01 — top-1 sense disambiguation (POC numbering).

Spec: N02/F18 DE-03. AC: US-01/AC-01. FT-anchors: FT-127.
BT-anchors: BT-083.

``pick_sense`` returns the highest-scored candidate plus an ``ambiguous``
flag set when the margin to the second-best candidate is below the
threshold. Threshold default is 0.2; the ``TIRVI_DISAMBIG_MARGIN`` env var
overrides it at call time (per design.md DE-03).
"""

from __future__ import annotations

import os

from tirvi.results import NLPToken

from .errors import DisambiguationError

_DEFAULT_MARGIN = 0.2
_ENV_VAR = "TIRVI_DISAMBIG_MARGIN"


def pick_sense(
    candidates: list[tuple[NLPToken, float]],
    margin_threshold: float | None = None,
) -> tuple[NLPToken, bool]:
    """Return ``(top_candidate, ambiguous)`` from a scored candidate list."""
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
