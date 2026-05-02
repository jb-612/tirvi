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

from tirvi.homograph.possessive_mappiq import apply_rule as _possessive_mappiq

from .client import diacritize_via_api
from .function_words import FUNCTION_WORD_LEXICON
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
    projected = _project_with_context(raw, nlp.tokens, sentence=text)
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
    entries: list[dict[str, Any]],
    tokens: list[NLPToken],
    sentence: str | None = None,
) -> str:
    parts: list[str] = []
    cursor = 0
    for entry in entries:
        if entry.get("sep"):
            parts.append(_pick(entry))
            continue
        token = tokens[cursor] if cursor < len(tokens) else None
        parts.append(_resolve_entry(entry, token, sentence))
        cursor += 1
    return "".join(parts)


def _resolve_entry(
    entry: dict[str, Any], token: NLPToken | None, sentence: str | None
) -> str:
    """ADR-038 — F51 rule layer first, then F19 NLP-context, else top-1."""
    rule_pick = _apply_context_rules(entry, sentence)
    if rule_pick is not None:
        return rule_pick
    return _pick_in_context(entry, token)


def _option_w(option: Any) -> str:
    """Extract the vocalized form ``w`` from either str or dict option."""
    if isinstance(option, dict):
        return str(option.get("w", ""))
    return str(option)


def _apply_context_rules(
    entry: dict[str, Any], sentence: str | None
) -> str | None:
    """Run F51 deterministic rules; return resolved string or None."""
    if not sentence:
        return None
    options = entry.get("options") or []
    str_options = [_option_w(o) for o in options if isinstance(o, (str, dict))]
    str_options = [s for s in str_options if s]
    if not str_options:
        return None
    word = str(entry.get("word", ""))
    pick = _possessive_mappiq(sentence, word, str_options)
    if pick is None:
        return None
    return str_options[pick - 1].replace(_PREFIX_MARKER, "")


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
    """ADR-039: a morph-bearing option is a dict carrying both ``w``
    (vocalized form) and ``lex`` (lemma). The undocumented ``morph``
    bitfield is not required — we score on lex + prefix_len."""
    return isinstance(option, dict) and "w" in option and "lex" in option


def _strip_nikud(text: str) -> str:
    return "".join(c for c in text if not 0x0591 <= ord(c) <= 0x05C7)


def _score_option(option: dict[str, Any], token: NLPToken) -> int:
    """Heuristic POS-fit score for a Dicta morph-shape option (ADR-039).

    Score 3 = strong fit (POS-specific signal lands).
    Score 2 = decent fit (verb pattern recognised).
    Score 1 = weak positive fit.
    Score 0 = no signal — top-1 wins via tie-break.
    """
    if not token.pos:
        return 0
    return _score_by_pos(option, token.pos)


def _score_by_pos(option: dict[str, Any], pos: str) -> int:
    if pos == "ADJ":
        return _score_adj(option)
    if pos in {"ADP", "SCONJ"}:
        return _score_function_word(option)
    if pos == "VERB":
        return _score_verb(option)
    if pos == "NOUN":
        return _score_noun(option)
    return 0


def _score_adj(option: dict[str, Any]) -> int:
    """Adjective: prefix_len=0 AND lex == w (canonical, no clitic)."""
    w = str(option.get("w", "")).replace(_PREFIX_MARKER, "")
    lex = str(option.get("lex", ""))
    if option.get("prefix_len", 0) == 0 and _strip_nikud(w) == _strip_nikud(lex):
        return 3
    return 0


def _score_function_word(option: dict[str, Any]) -> int:
    """Function word: lex is in the curated lexicon."""
    return 3 if option.get("lex", "") in FUNCTION_WORD_LEXICON else 0


def _score_verb(option: dict[str, Any]) -> int:
    """Verb: Dicta lemma uses '_' separator (e.g., 'קרא_פעל')."""
    return 2 if "_" in str(option.get("lex", "")) else 0


def _score_noun(option: dict[str, Any]) -> int:
    """Noun: prefix_len ≤ 1 AND lex is non-verb-shaped."""
    lex = str(option.get("lex", ""))
    if option.get("prefix_len", 0) <= 1 and "_" not in lex:
        return 1
    return 0


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

    Handles both bare-string options (``task: nakdan`` legacy) and
    dict-shape options (``task: morph`` per ADR-039) — extracts the
    ``w`` field for dicts, falls back to ``str()`` for strings.
    """
    options = entry.get("options") or []
    if not options:
        return word
    return _option_w(options[0]).replace(_PREFIX_MARKER, "")
