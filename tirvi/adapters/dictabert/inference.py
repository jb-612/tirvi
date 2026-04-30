"""F17 T-02 — DictaBERT inference + UD-Hebrew label mapping.

Spec: N02/F17 DE-02. AC: US-01/AC-01. FT-anchors: FT-124, FT-130.

Uses the DictaBERT-large-joint custom predict() head when available
(model.predict([text], tokenizer) returns ``[{"tokens": [{"token", "lex",
"syntax": {"pos": ...}}, ...]}]``).
"""

from __future__ import annotations

from typing import Any

from tirvi.results import NLPResult, NLPToken

from .loader import load_model

PROVIDER = "dictabert-large-joint"


def analyze(
    text: str,
    lang: str = "he",
    revision: str = "default",
) -> NLPResult:
    """Analyze a Hebrew sentence into UD tokens via DictaBERT-large-joint."""
    if not text.strip():
        return NLPResult(provider=PROVIDER, tokens=[], confidence=None)
    model, tokenizer = load_model(revision)
    tokens = _run_joint_predict(model, tokenizer, text)
    return NLPResult(provider=PROVIDER, tokens=tokens, confidence=None)


def _run_joint_predict(model: Any, tokenizer: Any, text: str) -> list[NLPToken]:
    """Invoke the DictaBERT joint head and decode the per-token output."""
    raw = model.predict([text], tokenizer)
    return [_decode_token(item) for item in raw[0]["tokens"]]


def _decode_token(item: dict[str, Any]) -> NLPToken:
    syntax = item.get("syntax") or {}
    return NLPToken(
        text=item["token"],
        pos=syntax.get("pos"),
        lemma=item.get("lex"),
    )
