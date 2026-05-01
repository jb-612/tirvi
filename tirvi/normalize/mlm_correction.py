"""DictaBERT-MLM-based OCR correction.

Replaces character-level errors using the masked language model's
sentence-level probability. For each suspicious word, generate
substitution candidates and pick the highest-scoring under DictaBERT.

This generalizes the hardcoded ם/ס fix list — any character-confusion
pair (ר↔ד, ה↔ח, ם↔ס, ן↔ו, ץ↔צ, ך↔כ, ף↔פ) is auto-tried.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

_log = logging.getLogger("tirvi.normalize.mlm")

# Common Tesseract heb_best confusion pairs. Order matters: most-likely first.
_OCR_CONFUSIONS: dict[str, list[str]] = {
    "ם": ["ס"], "ס": ["ם"],     # final mem ↔ samech
    "ן": ["ו"], "ו": ["ן"],     # final nun ↔ vav
    "ך": ["כ"], "כ": ["ך"],     # final kaf ↔ kaf
    "ף": ["פ"], "פ": ["ף"],     # final pe ↔ pe
    "ץ": ["צ"], "צ": ["ץ"],     # final tsadi ↔ tsadi
    "ר": ["ד"], "ד": ["ר"],     # resh ↔ dalet (visually similar)
    "ה": ["ח"], "ח": ["ה"],     # he ↔ chet (open vs closed top)
    "ב": ["כ"], "כ": ["ב"],     # bet ↔ kaf (legacy added below)
}

_MIN_DELTA_SCORE = 3.0   # candidate must beat original by this log-prob margin
_CONTEXT_WINDOW   = 4    # words on each side


@lru_cache(maxsize=1)
def _load():
    """Load DictaBERT MLM once per process. Returns (tokenizer, model)."""
    import torch
    from transformers import AutoModelForMaskedLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained("dicta-il/dictabert")
    model = AutoModelForMaskedLM.from_pretrained("dicta-il/dictabert")
    model.eval()
    if torch.backends.mps.is_available():
        model = model.to("mps")
    return tok, model


def correct_with_mlm(words: list[str]) -> list[str]:
    """For each word, if char-substitution candidates score higher under
    DictaBERT-MLM than the original, replace the original.
    """
    if not words:
        return words
    try:
        tok, model = _load()
    except Exception as e:
        _log.warning("DictaBERT MLM unavailable (%s) — skipping", e)
        return words

    out = list(words)
    for i, word in enumerate(out):
        if not _is_candidate_for_correction(word):
            continue
        candidates = _generate_candidates(word)
        if not candidates:
            continue
        ctx_prev = out[max(0, i - _CONTEXT_WINDOW):i]
        ctx_next = out[i + 1:i + 1 + _CONTEXT_WINDOW]
        best = _pick_best(word, candidates, ctx_prev, ctx_next, tok, model)
        if best != word:
            _log.info("MLM correction: %r → %r (context: %r ... %r)",
                      word, best, " ".join(ctx_prev[-2:]), " ".join(ctx_next[:2]))
            out[i] = best
    return out


def _is_candidate_for_correction(word: str) -> bool:
    """Skip pure-punctuation, very-short words, and words without confusable chars."""
    if len(word) < 2:
        return False
    if not any(ch in _OCR_CONFUSIONS for ch in word):
        return False
    return True


def _generate_candidates(word: str) -> list[str]:
    """All single-char-substitution candidates for known confusion pairs."""
    cands = []
    for i, ch in enumerate(word):
        for sub in _OCR_CONFUSIONS.get(ch, []):
            cands.append(word[:i] + sub + word[i + 1:])
    return cands


def _pick_best(orig: str, candidates: list[str],
               prev: list[str], nxt: list[str], tok, model) -> str:
    """Return the candidate (or orig) with highest MLM log-prob in context.

    Hard gates to avoid over-correction:
      - if orig is in Nakdan's word list → keep orig (valid Hebrew word).
      - candidate must be in Nakdan's word list (real Hebrew word).
      - candidate's MLM score must beat orig's by ``_MIN_DELTA_SCORE``.
    """
    if not _nakdan_rejects(orig):
        return orig                          # original is a valid word — leave it

    ctx_left = " ".join(prev)
    ctx_right = " ".join(nxt)
    valid_candidates = [c for c in candidates if not _nakdan_rejects(c)]
    if not valid_candidates:
        return orig                          # no real-word substitute found

    orig_score = _mlm_score(orig, ctx_left, ctx_right, tok, model)
    scores = {c: _mlm_score(c, ctx_left, ctx_right, tok, model) for c in valid_candidates}
    best = max(scores, key=scores.get)
    if scores[best] - orig_score >= _MIN_DELTA_SCORE:
        return best
    return orig


@lru_cache(maxsize=4096)
def _nakdan_rejects(word: str) -> bool:
    """True when Nakdan flags the word as not from its lexicon."""
    try:
        from tirvi.adapters.nakdan.client import diacritize_via_api
        entries = diacritize_via_api(word)
        for entry in entries:
            if not entry.get("sep"):
                return bool(entry.get("fnotfromwl"))
        return False
    except Exception:
        return False


def _mlm_score(word: str, ctx_left: str, ctx_right: str, tok, model) -> float:
    """Sum of log-probs of all tokens in `word` given left+right context.

    Builds: ``{ctx_left} [MASK]...[MASK] {ctx_right}`` (one MASK per sub-token
    in the word), and reads back the probability of each sub-token.
    """
    import torch

    # Sub-tokenise the candidate word
    word_ids = tok.encode(word, add_special_tokens=False)
    if not word_ids:
        return -1e9

    # Build masked input
    n_masks = len(word_ids)
    mask = " ".join([tok.mask_token] * n_masks)
    text = f"{ctx_left} {mask} {ctx_right}".strip()

    inputs = tok(text, return_tensors="pt")
    if model.device.type == "mps":
        inputs = {k: v.to("mps") for k, v in inputs.items()}

    mask_positions = (inputs["input_ids"][0] == tok.mask_token_id).nonzero().squeeze(-1)
    if mask_positions.numel() != n_masks:
        return -1e9

    with torch.no_grad():
        logits = model(**inputs).logits

    # Sum log-prob of the actual word_ids at each mask position
    log_probs = torch.log_softmax(logits[0, mask_positions], dim=-1)
    score = float(sum(log_probs[i, tid].item() for i, tid in enumerate(word_ids)))
    return score
