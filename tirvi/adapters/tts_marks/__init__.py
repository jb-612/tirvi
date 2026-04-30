"""F30 — TTS-emitted-timing adapter (slot of F03's WordTimingProvider).

Implements :class:`tirvi.ports.WordTimingProvider` via projection of
F26's :class:`tirvi.results.TTSResult.word_marks` into per-token start/end
seconds. Forced-alignment slot (ADR-015) deferred to F31.

Spec: N03/F30. Bounded context: ``bc:audio_delivery``.
"""

__all__: list[str] = []
