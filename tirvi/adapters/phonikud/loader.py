"""F20 T-01 — Phonikud lazy loader with optional fallback.

Spec: N02/F20 DE-01, ADR-022. AC: US-01/AC-01.

Vendor boundary: ``phonikud`` is allowed only inside ``tirvi.adapters.**``
(DE-06, ADR-014, ADR-022). The package is optional: when missing, the
loader returns ``None`` and downstream code routes to
:func:`fallback_g2p` (an identity transliterator that keeps the surface
text as the IPA hint). Per ADR-022 this is the deliberate degraded path
for environments where phonikud cannot install (e.g., older glibc).
"""

from __future__ import annotations

from functools import lru_cache
from types import ModuleType

from tirvi.results import G2PResult

PROVIDER = "phonikud"
FALLBACK_PROVIDER = "phonikud-fallback"


@lru_cache(maxsize=1)
def load_phonikud() -> ModuleType | None:
    """Lazily import ``phonikud`` and cache the module reference.

    Returns ``None`` when phonikud is not installed (degraded path).
    """
    try:
        import phonikud  # type: ignore[import-not-found]
    except ImportError:
        return None
    module: ModuleType = phonikud
    return module


def is_available() -> bool:
    return load_phonikud() is not None


def fallback_g2p(text: str) -> G2PResult:
    """Identity G2P used when phonikud is unavailable (ADR-022).

    Emits the surface text as a single phoneme entry; ``confidence=None``
    per biz S01 (None ≠ 0.0). Downstream consumers detect the degraded
    path via ``result.provider == "phonikud-fallback"``.
    """
    phonemes = [text] if text.strip() else []
    return G2PResult(provider=FALLBACK_PROVIDER, phonemes=phonemes, confidence=None)
