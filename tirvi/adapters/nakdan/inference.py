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

from tirvi.results import DiacritizationResult

from .client import diacritize_via_api
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


def _project_response(entries: list[dict[str, Any]]) -> str:
    """Concatenate top-pick diacritized strings, stripping prefix markers."""
    parts: list[str] = [_pick(entry) for entry in entries]
    return "".join(parts)


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
    """Top option (prefix marker stripped) when confident; else word."""
    options = entry.get("options") or []
    if not options or not entry.get("fconfident", True):
        return word
    return str(options[0]).replace(_PREFIX_MARKER, "")
