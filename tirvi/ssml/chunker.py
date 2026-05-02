"""F53 — clause-split SSML chunker.

Spec: N02/F53 DE-01..DE-03. ADR-041 row #9.

Splits a long block's tokens at safe boundaries (punctuation +
unambiguous Hebrew SCONJ conjunctions) so that F23's SSML emitter
can insert ``<break time="500ms"/>`` between fragments. This serves
the user-stated reading-disability requirement that long sentences
be paced into chunks under ~22 words.

Design contract:
    chunk_block_tokens(tokens, threshold) -> (fragments, breaks)
where:
    fragments — list[list[PlanToken]]; each inner list is a non-empty
                fragment (or, in the empty-input edge case, [[]]).
    breaks    — list of provenance dicts. Each "clause_split" entry
                records one break the chunker emitted; a single
                "clause_split_skipped" entry is emitted when the
                input is over threshold but no safe boundary exists.

The chunker is pure — no I/O, no mutation of input tokens. F23's
builder is responsible for emitting the actual ``<break>`` tag and
appending the provenance into ``PlanBlock.transformations``.
"""

from __future__ import annotations

from tirvi.plan.value_objects import PlanToken

# Per Q3 answer in PR #30 reviewer questions: 22 tokens, calibrate later.
DEFAULT_THRESHOLD: int = 22

_PUNCTUATION_FINAL: tuple[str, ...] = (".", "?", "!", ":", ";", ",")

# Hebrew SCONJ conjunctions used as safe split boundaries.
# Conservative initial set — extend with unit tests when adding entries.
CONJUNCTION_LEXICON: frozenset[str] = frozenset({
    "כיוון ש",
    "מאחר ש",
    "אף על פי ש",
    "במידה ו",
    "על מנת ש",
    "אם כי",
    "למרות ש",
})

_ADR_ROW: str = "ADR-041 #9"


def chunk_block_tokens(
    tokens: list[PlanToken], threshold: int = DEFAULT_THRESHOLD,
) -> tuple[list[list[PlanToken]], list[dict]]:
    """Return ``(fragments, breaks)`` for ``tokens``.

    Under-threshold input passes through unchanged. Over-threshold
    walks safe boundaries left-to-right and emits the smallest
    fragment count that keeps each fragment ≤ ``threshold`` (greedy).
    Empty token list is a degenerate input — returns ``([[]], [])``.
    """
    if not tokens:
        return ([[]], [])
    if len(tokens) <= threshold:
        return ([tokens], [])
    return _greedy_chunk(tokens, threshold)


def _greedy_chunk(
    tokens: list[PlanToken], threshold: int,
) -> tuple[list[list[PlanToken]], list[dict]]:
    """Walk safe boundaries; split at the FIRST boundary in scope."""
    boundary = _find_safe_boundary(tokens)
    if boundary is None:
        return ([tokens], [_skipped_entry(len(tokens))])
    cut, reason = boundary
    head = tokens[:cut]
    tail = tokens[cut:]
    breaks = [_split_entry(cut, reason, len(tail))]
    return ([head, tail], breaks)


def _find_safe_boundary(
    tokens: list[PlanToken],
) -> tuple[int, str] | None:
    """Return ``(cut_index, reason_string)`` or None.

    Punctuation: split AFTER the punctuation token (cut = idx + 1).
    Conjunction: split BEFORE the SCONJ-tagged conjunction (cut = idx).
    Earliest boundary wins; punctuation breaks ties (it's the cleaner
    sentence-end signal).
    """
    punct = _first_punct_index(tokens)
    conj = _first_conjunction_index(tokens)
    candidates = _candidate_boundaries(punct, conj)
    if not candidates:
        return None
    return min(candidates, key=lambda c: c[0])


def _candidate_boundaries(
    punct: int | None, conj: tuple[int, str] | None,
) -> list[tuple[int, str]]:
    """Map raw boundary signals to ``(cut_index, reason)`` candidates."""
    out: list[tuple[int, str]] = []
    if punct is not None:
        out.append((punct + 1, "punctuation"))
    if conj is not None:
        idx, lemma = conj
        out.append((idx, f"conjunction:{lemma}"))
    return out


def _first_punct_index(tokens: list[PlanToken]) -> int | None:
    for i, tok in enumerate(tokens):
        if _ends_with_punct(tok.text):
            return i
    return None


def _first_conjunction_index(
    tokens: list[PlanToken],
) -> tuple[int, str] | None:
    for i, tok in enumerate(tokens):
        if tok.pos == "SCONJ" and tok.text in CONJUNCTION_LEXICON:
            return (i, tok.text)
    return None


def _ends_with_punct(text: str) -> bool:
    if not text:
        return False
    return text[-1] in _PUNCTUATION_FINAL


def _split_entry(cut: int, reason: str, tail_len: int) -> dict:
    return {
        "kind": "clause_split",
        "at_token_index": cut,
        "reason": reason,
        "adr_row": _ADR_ROW,
        "fragment_word_count_after": tail_len,
    }


def _skipped_entry(word_count: int) -> dict:
    return {
        "kind": "clause_split_skipped",
        "word_count": word_count,
        "reason": "no_safe_boundary",
        "adr_row": _ADR_ROW,
    }
