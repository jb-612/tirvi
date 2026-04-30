"""F17 — DictaBERT NLP adapter.

Implements :class:`tirvi.ports.NLPBackend` using HuggingFace ``transformers``
for Hebrew UD tokenization + POS tagging.

Vendor isolation: this module is the only place ``transformers`` /
``huggingface_hub`` may be imported (DE-06, ADR-014, ADR-020).

Spec: N02/F17. Bounded context: ``bc:hebrew_nlp``.
"""

__all__: list[str] = []
