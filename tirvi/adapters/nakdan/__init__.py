"""F19 — Dicta-Nakdan diacritization adapter.

Implements :class:`tirvi.ports.DiacritizerBackend` using HuggingFace
``transformers`` (AutoModelForSeq2SeqLM) for Hebrew nikud insertion.

Vendor isolation: this module is the only place ``transformers`` may be
imported for diacritization (DE-06, ADR-014, ADR-021).

Spec: N02/F19. Bounded context: ``bc:pronunciation``.
"""

__all__: list[str] = []
