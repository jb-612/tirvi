"""DictaBERTAdapter — :class:`tirvi.ports.NLPBackend` implementation.

Spec: N02/F17 DE-06. AC: US-01/AC-01, US-02/AC-01.

Happy path: DictaBERT inference (provider="dictabert-morph").
Fallback: AlephBertYapFallbackAdapter (F26) on ImportError/OSError.
Degraded: NLPResult(provider="degraded") when F26 is also unavailable.
"""

from __future__ import annotations

import importlib

from tirvi.ports import NLPBackend
from tirvi.results import NLPResult

from .inference import analyze as _analyze

_F26_MODULE = "tirvi.adapters.alephbert"
_F26_CLASS = "AlephBertYapFallbackAdapter"
_DEGRADED = NLPResult(provider="degraded", tokens=[], confidence=None)


class DictaBERTAdapter(NLPBackend):
    """DictaBERT-based Hebrew NLP adapter with F26 graceful fallback."""

    def __init__(self, model_revision: str = "default") -> None:
        self._model_revision = model_revision
        self._f26_adapter: NLPBackend | None = None

    def analyze(self, text: str, lang: str) -> NLPResult:
        try:
            return _analyze(text, lang=lang, revision=self._model_revision)
        except (ImportError, OSError):
            return self._f26_analyze(text, lang)

    def _f26_analyze(self, text: str, lang: str) -> NLPResult:
        if self._f26_adapter is None:
            self._f26_adapter = self._load_f26()
        if self._f26_adapter is None:
            return _DEGRADED
        return self._f26_adapter.analyze(text, lang)

    def _load_f26(self) -> NLPBackend | None:
        try:
            mod = importlib.import_module(_F26_MODULE)
            cls = getattr(mod, _F26_CLASS)
            return cls()
        except ImportError:
            return None
