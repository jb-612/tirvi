"""DictaBERTAdapter — :class:`tirvi.ports.NLPBackend` implementation.

Spec: N02/F17. AC: US-01/AC-01.
"""

from tirvi.ports import NLPBackend
from tirvi.results import NLPResult


class DictaBERTAdapter(NLPBackend):
    """DictaBERT-based Hebrew NLP adapter.

    Invariants (named, TDD fills):
      - INV-DICTA-001 (DE-01, ADR-020): module-level LRU-cached model load
      - INV-DICTA-002 (DE-02): pinned model revision + UD-Hebrew label mapper
      - INV-DICTA-005 (DE-06, ADR-014): vendor SDK imports stay in this module
    """

    def __init__(self, model_revision: str = "default") -> None:
        # TODO US-01/AC-01: lazy-init transformers model + tokenizer
        self._model_revision = model_revision

    def analyze(self, text: str, lang: str) -> NLPResult:
        # TODO INV-DICTA-001: load_model() with module-level LRU cache
        # TODO INV-DICTA-002: tokenize, predict POS, map UD labels
        raise NotImplementedError
