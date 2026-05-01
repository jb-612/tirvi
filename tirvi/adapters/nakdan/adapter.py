"""DictaNakdanAdapter — :class:`tirvi.ports.DiacritizerBackend` implementation.

Spec: N02/F19. AC: US-01/AC-01.
"""

from tirvi.ports import DiacritizerBackend
from tirvi.results import DiacritizationResult, NLPResult

from .inference import diacritize as _diacritize
from .inference import diacritize_in_context as _diacritize_in_context


class DictaNakdanAdapter(DiacritizerBackend):
    """Dicta-Nakdan-based diacritization adapter.

    Invariants (named, TDD fills):
      - INV-NAKDAN-001 (DE-01, ADR-025): HTTP I/O confined to client.py submodule
      - INV-NAKDAN-002 (DE-02): NLP context scoring picks among Dicta response options
      - INV-NAKDAN-003 (DE-05): unconditional NFC→NFD nikud normalization
      - INV-NAKDAN-006 (DE-06, ADR-029): Dicta endpoint URL constant lives only in client.py
    """

    def __init__(self, model_revision: str = "default") -> None:
        self._model_revision = model_revision

    def diacritize(self, text: str) -> DiacritizationResult:
        return _diacritize(text, revision=self._model_revision)

    def diacritize_in_context(self, text: str, nlp: NLPResult) -> DiacritizationResult:
        """NLP-aware variant — uses POS + morph to pick among Nakdan candidates."""
        return _diacritize_in_context(text, nlp)
