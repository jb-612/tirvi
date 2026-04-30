"""F26 — Google Wavenet TTS adapter.

Implements :class:`tirvi.ports.TTSBackend` using ``google-cloud-texttospeech``
(v1beta1 — required for ``timepoints`` aka SSML marks). POC voice:
``he-IL-Wavenet-D``.

Vendor isolation: this module is the only place ``google.cloud`` may be
imported (DE-06, ADR-014).

Spec: N03/F26. Bounded context: ``bc:speech_synthesis``.
"""

__all__: list[str] = []
