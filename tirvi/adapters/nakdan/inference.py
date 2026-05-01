"""F19 T-03 (per ADR-025) — Nakdan inference via Dicta REST.

Spec: N02/F19 DE-03. AC: US-01/AC-01. FT-anchors: FT-150.

Pivots from in-process seq2seq (ADR-021, deprecated for POC) to the
Dicta public REST endpoint (ADR-025). The client lives in
``.client``; this module is responsible for projecting the per-word
response into a single diacritized string and applying NFD
normalization (T-05) before returning a DiacritizationResult.
"""

from __future__ import annotations

from typing import Any

from tirvi.results import DiacritizationResult, NLPResult, NLPToken

from .client import diacritize_via_api
from .normalize import to_nfd
from .overrides import HOMOGRAPH_OVERRIDES

PROVIDER = "dicta-nakdan-rest"

_PREFIX_MARKER = "|"


def diacritize(text: str, revision: str = "default") -> DiacritizationResult:
    """Insert nikud into Hebrew ``text`` via the Dicta REST API."""
    if not text.strip():
        return DiacritizationResult(provider=PROVIDER, diacritized_text="", confidence=None)
    raw = diacritize_via_api(text)
    projected = _project_response(raw)
    return DiacritizationResult(
        provider=PROVIDER,
        diacritized_text=to_nfd(projected),
        confidence=None,
    )


def diacritize_in_context(text: str, nlp: NLPResult) -> DiacritizationResult:
    """T-02: NLP-context-aware diacritization.

    For each Dicta entry whose options carry a morphology signal, pick
    the option whose morph best matches the aligned NLP token. Falls
    through to :func:`_pick` when no signal is available.
    """
    if not text.strip():
        return DiacritizationResult(provider=PROVIDER, diacritized_text="", confidence=None)
    raw = diacritize_via_api(text)
    projected = _project_with_context(raw, nlp.tokens)
    return DiacritizationResult(
        provider=PROVIDER,
        diacritized_text=to_nfd(projected),
        confidence=None,
    )


def _project_response(entries: list[dict[str, Any]]) -> str:
    """Concatenate top-pick diacritized strings, stripping prefix markers."""
    parts: list[str] = [_pick(entry) for entry in entries]
    return "".join(parts)


def _project_with_context(
    entries: list[dict[str, Any]], tokens: list[NLPToken]
) -> str:
    parts: list[str] = []
    cursor = 0
    for entry in entries:
        if entry.get("sep"):
            parts.append(_pick(entry))
            continue
        token = tokens[cursor] if cursor < len(tokens) else None
        parts.append(_pick_in_context(entry, token))
        cursor += 1
    return "".join(parts)


def _pick_in_context(entry: dict[str, Any], token: NLPToken | None) -> str:
    """Score morph-bearing options against ``token``; else fall through."""
    if token is None:
        return _pick(entry)
    morph_options = [opt for opt in entry.get("options") or [] if _is_morph_option(opt)]
    if not morph_options:
        return _pick(entry)
    best = max(morph_options, key=lambda opt: _score_option(opt, token))
    return str(best["w"]).replace(_PREFIX_MARKER, "")


def _is_morph_option(option: Any) -> bool:
    return isinstance(option, dict) and "w" in option and "morph" in option


def _score_option(option: dict[str, Any], token: NLPToken) -> int:
    morph = option.get("morph") or {}
    return _pos_score(morph, token.pos) + _morph_keys_score(morph, token.morph_features)


def _pos_score(morph: dict[str, Any], pos: str | None) -> int:
    return 2 if pos and morph.get("pos") == pos else 0


def _morph_keys_score(morph: dict[str, Any], nlp_morph: dict[str, str] | None) -> int:
    return sum(1 for k, v in (nlp_morph or {}).items() if morph.get(k) == v)


def _pick(entry: dict[str, Any]) -> str:
    """Resolve one Dicta entry to its emitted form.

    Priority chain (per ADR-025 + Round-2 review): sep → override → empty
    options → confidence-gated top option → undecorated fallback.
    Implemented as short-circuiting helper predicates so the dispatch
    stays at CC ≤ 3 with headroom for T-02's NLP-context branch.
    """
    word = str(entry.get("word", ""))
    return (
        _passthrough(entry, word)
        or _override_hit(word)
        or _confidence_gated(entry, word)
    )


def _passthrough(entry: dict[str, Any], word: str) -> str | None:
    """Return the raw word for separator entries (whitespace/punct)."""
    return word if entry.get("sep") else None


def _override_hit(word: str) -> str | None:
    """Return the F21 lexicon override for ``word`` if registered."""
    return HOMOGRAPH_OVERRIDES.get(word)


def _confidence_gated(entry: dict[str, Any], word: str) -> str:
    """Pick top diacritized option even when confidence is low.

    Previously: returned raw (un-vocalized) word when fconfident=False, which
    left most words without nikud and broke TTS pronunciation. Now: always
    pick the top option (Nakdan's best guess) — _pick_in_context uses NLP
    tokens to override this when context is available.
    """
    options = entry.get("options") or []
    if not options:
        return word
    return str(options[0]).replace(_PREFIX_MARKER, "")
