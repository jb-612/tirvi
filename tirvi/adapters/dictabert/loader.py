"""F17 T-01 — DictaBERT module-level LRU loader.

Spec: N02/F17 DE-01, ADR-020. AC: US-01/AC-01.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

_MODEL_NAME = "dicta-il/dictabert-joint"
_DEFAULT_REVISION = "default"


def _resolved_revision(revision: str) -> str | None:
    if revision == _DEFAULT_REVISION:
        return os.environ.get("TIRVI_DICTABERT_REVISION") or None
    return revision


@lru_cache(maxsize=2)
def load_model(revision: str = _DEFAULT_REVISION) -> tuple[Any, Any]:
    """Return ``(model, tokenizer)`` for dictabert-joint, loaded once per process."""
    from transformers import AutoModel, AutoTokenizer  # type: ignore[import-not-found]

    rev = _resolved_revision(revision)
    tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME, revision=rev)
    model = AutoModel.from_pretrained(
        _MODEL_NAME, revision=rev, trust_remote_code=True
    )
    model.eval()
    return model, tokenizer
