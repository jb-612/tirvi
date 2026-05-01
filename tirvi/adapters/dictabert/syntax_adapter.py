"""DictaBERT-syntax adapter — dependency tree NLP backend."""
from __future__ import annotations
from functools import lru_cache
from typing import Any
from tirvi.ports import NLPBackend
from tirvi.results import NLPResult, NLPToken

PROVIDER = "dictabert-syntax"
_MODEL  = "dicta-il/dictabert-syntax"


@lru_cache(maxsize=1)
def _load():
    from transformers import AutoModel, AutoTokenizer  # type: ignore
    tok   = AutoTokenizer.from_pretrained(_MODEL)
    model = AutoModel.from_pretrained(_MODEL, trust_remote_code=True)
    model.eval()
    return model, tok


class DictaBERTSyntaxAdapter(NLPBackend):
    """NLPBackend that returns dependency-tree annotations from dictabert-syntax."""

    def analyze(self, text: str, lang: str = "he") -> NLPResult:
        if not text.strip():
            return NLPResult(provider=PROVIDER, tokens=[])
        try:
            model, tok = _load()
            result = model.predict([text], tok)
            tokens = [_dep_to_token(d) for d in (result[0].get("tree") or [])]
            return NLPResult(provider=PROVIDER, tokens=tokens)
        except (ImportError, OSError):
            return NLPResult(provider="degraded", tokens=[])


def _dep_to_token(dep: dict[str, Any]) -> NLPToken:
    morph = {"dep_func": dep.get("dep_func", ""), "dep_head": dep.get("dep_head", "")}
    return NLPToken(text=dep.get("word", ""), morph_features=morph)
