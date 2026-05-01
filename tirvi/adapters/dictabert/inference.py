"""F17 T-02 + T-05 — DictaBERT inference + long-sentence chunking.

Spec: N02/F17 DE-02, DE-05. AC: US-01/AC-01. FT-anchors: FT-124, FT-130.

Uses the DictaBERT-large-joint custom predict() head when available
(model.predict([text], tokenizer) returns ``[{"tokens": [{"token", "lex",
"syntax": {"pos": ...}}, ...]}]``). Long inputs are split on sub-token
count with overlap-merge left-chunk-wins strategy (DE-05).
"""

from __future__ import annotations

from typing import Any

from tirvi.results import NLPResult, NLPToken

from .loader import load_model

PROVIDER = "dictabert-morph"

_MAX_SUBTOKENS = 448
_OVERLAP_SUBTOKENS = 64


def analyze(
    text: str,
    lang: str = "he",
    revision: str = "default",
) -> NLPResult:
    """Analyze a Hebrew sentence into UD tokens via DictaBERT-large-joint."""
    if not text.strip():
        return NLPResult(provider=PROVIDER, tokens=[], confidence=None)
    model, tokenizer = load_model(revision)
    tokens = _run_joint_predict_chunked(model, tokenizer, text)
    return NLPResult(provider=PROVIDER, tokens=tokens, confidence=None)


def _run_joint_predict(model: Any, tokenizer: Any, text: str) -> list[NLPToken]:
    """Invoke the DictaBERT joint head and decode the per-token output."""
    raw = model.predict([text], tokenizer)
    return [_decode_token(item) for item in raw[0]["tokens"]]


def _run_joint_predict_chunked(
    model: Any, tokenizer: Any, text: str
) -> list[NLPToken]:
    """Predict with chunking when the input exceeds the model context window."""
    encoded = tokenizer.encode(text, add_special_tokens=False)
    if len(encoded) <= _MAX_SUBTOKENS:
        return _run_joint_predict(model, tokenizer, text)
    words = text.split()
    word_subcounts = [
        len(tokenizer.encode(w, add_special_tokens=False)) for w in words
    ]
    chunk_ranges = _compute_chunks(
        word_subcounts, _MAX_SUBTOKENS, _OVERLAP_SUBTOKENS
    )
    candidates = _collect_chunk_predictions(
        model, tokenizer, words, chunk_ranges
    )
    return _reconcile_overlap(candidates)


def _compute_chunks(
    word_subcounts: list[int],
    max_subtokens: int,
    overlap_subtokens: int,
) -> list[tuple[int, int]]:
    """Return [(start, end)) word-index pairs covering all words with overlap."""
    chunks: list[tuple[int, int]] = []
    n = len(word_subcounts)
    start = 0
    while start < n:
        end = _scan_chunk_end(word_subcounts, start, max_subtokens)
        chunks.append((start, end))
        if end >= n:
            break
        start = _find_overlap_start(word_subcounts, end, overlap_subtokens)
    return chunks


def _scan_chunk_end(
    word_subcounts: list[int], start: int, max_subtokens: int
) -> int:
    """Walk forward from ``start`` while the running sub-token sum fits."""
    end = start
    running = 0
    n = len(word_subcounts)
    while end < n and running + word_subcounts[end] <= max_subtokens:
        running += word_subcounts[end]
        end += 1
    if end == start:
        # Single word exceeds the cap; force-include it to make progress.
        end = start + 1
    return end


def _find_overlap_start(
    word_subcounts: list[int], chunk_end: int, overlap_subtokens: int
) -> int:
    """Walk backward from ``chunk_end`` summing words up to the overlap budget."""
    accum = 0
    i = chunk_end - 1
    while i >= 0 and accum + word_subcounts[i] <= overlap_subtokens:
        accum += word_subcounts[i]
        i -= 1
    next_start = i + 1
    if next_start >= chunk_end:
        next_start = chunk_end - 1
    return next_start


def _collect_chunk_predictions(
    model: Any,
    tokenizer: Any,
    words: list[str],
    chunk_ranges: list[tuple[int, int]],
) -> list[list[NLPToken]]:
    """Run ``predict`` per chunk and bucket results by global word index."""
    per_word: list[list[NLPToken]] = [[] for _ in words]
    for start, end in chunk_ranges:
        chunk_text = " ".join(words[start:end])
        chunk_tokens = _run_joint_predict(model, tokenizer, chunk_text)
        for offset, tok in enumerate(chunk_tokens):
            per_word[start + offset].append(tok)
    return per_word


def _reconcile_overlap(candidates: list[list[NLPToken]]) -> list[NLPToken]:
    """Pick one NLPToken per word; left-chunk-wins for overlap regions."""
    return [tokens[0] for tokens in candidates]


def _decode_token(item: dict[str, Any]) -> NLPToken:
    syntax = item.get("syntax") or {}
    prefix_raw = item.get("prefix_segments")
    prefix = tuple(prefix_raw) if prefix_raw else None
    return NLPToken(
        text=item["token"],
        pos=syntax.get("pos"),
        lemma=item.get("lex"),
        prefix_segments=prefix,
        confidence=item.get("confidence"),
    )
