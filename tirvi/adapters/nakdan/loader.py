"""F19 T-01 — Dicta-Nakdan model loader (LRU-cached).

Spec: N02/F19 DE-01, ADR-021. AC: US-01/AC-01. BT-anchors: BT-099.

Vendor boundary: ``transformers`` and ``torch`` are allowed only inside
``tirvi.adapters.**`` (DE-06, ADR-021, ADR-029). Mirrors the F17 loader
pattern. Adds a ``release_cache`` helper to free GPU memory between
heavy stages (no-op on CPU).
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

_MODEL_NAME = "dicta-il/dicta-nakdan"
_DEFAULT_REVISION = "default"


def _resolved_revision(revision: str) -> str | None:
    if revision == _DEFAULT_REVISION:
        return os.environ.get("TIRVI_NAKDAN_REVISION") or None
    return revision


@lru_cache(maxsize=2)
def load_model(revision: str = _DEFAULT_REVISION) -> tuple[Any, Any]:
    """Return ``(model, tokenizer)`` for Dicta-Nakdan, lazily.

    Vendor imports are deferred inside this function so the module can be
    imported without ``transformers``/``torch`` installed (ADR-029).
    """
    from transformers import (  # type: ignore[import-not-found]
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
    )

    rev = _resolved_revision(revision)
    model = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME, revision=rev)
    tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME, revision=rev)
    return model, tokenizer


def release_cache() -> None:
    """Release CUDA memory between pipeline stages (idempotent on CPU)."""
    try:
        import torch  # type: ignore[import-not-found]
    except ImportError:
        return
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
