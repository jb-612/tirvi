"""DictaNakdanAdapter — :class:`tirvi.ports.DiacritizerBackend` implementation.

Spec: N02/F19. AC: US-01/AC-01.
"""

from tirvi.ports import DiacritizerBackend
from tirvi.results import DiacritizationResult

from .inference import diacritize as _diacritize


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
