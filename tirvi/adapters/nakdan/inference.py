"""F19 T-03 — Nakdan seq2seq inference.

Spec: N02/F19 DE-03. AC: US-01/AC-01. FT-anchors: FT-150.

Wraps the Dicta-Nakdan model in a single-pass call, normalizes the
diacritized output through NFC→NFD (T-05), and forwards a confidence
score (top-1 vs. top-2 softmax margin per design.md).
"""

from __future__ import annotations

from typing import Any

from tirvi.results import DiacritizationResult

from .loader import load_model
from .normalize import to_nfd

PROVIDER = "dicta-nakdan"


def diacritize(text: str, revision: str = "default") -> DiacritizationResult:
    """Insert nikud into Hebrew ``text`` via Dicta-Nakdan."""
    if not text.strip():
        return DiacritizationResult(provider=PROVIDER, diacritized_text="", confidence=None)
    model, tokenizer = load_model(revision)
    raw = _run_diacritization(model, tokenizer, text)
    return DiacritizationResult(
        provider=PROVIDER,
        diacritized_text=to_nfd(str(raw["diacritized"])),
        confidence=raw.get("confidence"),
    )


def _run_diacritization(model: Any, tokenizer: Any, text: str) -> dict[str, Any]:
    """Invoke the Nakdan custom predict head and return the raw response.

    Tests patch this function with canned output; production calls
    ``model.predict([text], tokenizer)`` and consumes the first element.
    """
    response = model.predict([text], tokenizer)
    return dict(response[0])
