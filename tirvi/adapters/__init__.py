"""Vendor-bound adapters (F03 DE-06 boundary anchor).

This package is the **only** place vendor SDKs may be imported. The ruff
``flake8-tidy-imports`` banned-api rule (see ``ruff.toml``) blocks
``google.cloud``, ``transformers``, ``torch``, and ``huggingface_hub`` from
every other path under ``tirvi/``; ``tirvi/adapters/**`` is whitelisted.

Concrete adapters land in feature-specific submodules:

  - F08: Tesseract ``OCRBackend`` adapter
  - F17: DictaBERT ``NLPBackend`` adapter
  - F19: Dicta-Nakdan ``DiacritizerBackend`` adapter
  - F20: Phonikud ``G2PBackend`` adapter
  - F26: Google Wavenet ``TTSBackend`` adapter
  - F30: TTS-emitted timing ``WordTimingProvider`` adapter
"""

__all__: list[str] = []
