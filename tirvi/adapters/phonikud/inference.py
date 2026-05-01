"""F20 T-02 — Phonikud whole-text IPA via ``phonemize`` (per ADR-028).

Spec: N02/F20 DE-02. AC: US-01/AC-01.
FT-anchors: FT-152, FT-154, FT-157. BT-anchors: BT-101.

Whole-text IPA via phonikud's ``phonemize`` API with inline stress and
vocal-shva prediction (``predict_vocal_shva=True``). Returns a single
IPA string wrapped in a 1-element list so the G2PResult shape stays
stable across providers. When phonikud is unavailable (ADR-022
degraded path), :func:`fallback_g2p` returns the input text as a
single phoneme so downstream stages keep running.
"""

from __future__ import annotations

from typing import Any

from tirvi.results import G2PResult

from .loader import PROVIDER, fallback_g2p, load_phonikud


def grapheme_to_phoneme(text: str, lang: str = "he") -> G2PResult:
    """Convert Hebrew (typically diacritized) ``text`` to whole-text IPA."""
    if not text.strip():
        return G2PResult(provider=PROVIDER, phonemes=[], confidence=None)
    module = load_phonikud()
    if module is None:
        return fallback_g2p(text)
    return _emit(module, text)


def _emit(module: Any, text: str) -> G2PResult:
    ipa = str(module.phonemize(text, predict_vocal_shva=True))
    phonemes = [ipa] if ipa else []
    return G2PResult(provider=PROVIDER, phonemes=phonemes, confidence=None)
