"""F17 T-01 — DictaBERT module-level LRU loader.

Spec: N02/F17 DE-01, ADR-020. AC: US-01/AC-01. FT-anchors: FT-125.
BT-anchors: BT-086.

Vendor boundary: ``transformers`` and ``huggingface_hub`` are allowed only
inside ``tirvi.adapters.**`` (DE-06, ADR-014, ADR-020). Module-level
``functools.lru_cache`` ensures the model is loaded once per process per
revision pin.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

_MODEL_NAME = "dicta-il/dictabert-large-joint"
_DEFAULT_REVISION = "default"


def _resolved_revision(revision: str) -> str | None:
    if revision == _DEFAULT_REVISION:
        return os.environ.get("TIRVI_DICTABERT_REVISION") or None
    return revision


@lru_cache(maxsize=2)
def load_model(revision: str = _DEFAULT_REVISION) -> tuple[Any, Any]:
    """Return ``(model, tokenizer)`` for DictaBERT-large-joint, lazily.

    Pinned revision via the ``TIRVI_DICTABERT_REVISION`` env var when
    ``revision == "default"`` (per ADR-020). Vendor imports are deferred
    inside this function so the module can be imported without
    ``transformers`` installed (ADR-014 vendor boundary).
    """
    from transformers import (  # type: ignore[import-not-found]
        AutoModelForTokenClassification,
        AutoTokenizer,
    )

    rev = _resolved_revision(revision)
    model = AutoModelForTokenClassification.from_pretrained(_MODEL_NAME, revision=rev)
    tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME, revision=rev)
    return model, tokenizer
