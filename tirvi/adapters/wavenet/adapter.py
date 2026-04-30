"""WavenetTTSAdapter — :class:`tirvi.ports.TTSBackend` implementation.

Spec: N03/F26. AC: US-01/AC-01.
"""

from typing import Any

from tirvi.ports import TTSBackend
from tirvi.results import TTSResult

from .assembly import assemble_tts_result
from .client import POC_VOICE, build_client


class WavenetTTSAdapter(TTSBackend):
    """Google Wavenet TTS adapter (he-IL voices) using v1beta1 ``timepoints``.

    Invariants:
      - INV-WAVENET-001 (DE-01): uses v1beta1 client to receive ``timepoints``
      - INV-WAVENET-002 (DE-02): default voice = ``he-IL-Wavenet-D`` for POC
      - INV-WAVENET-003 (DE-03): timepoints parsed into :class:`tirvi.results.WordMark`
      - INV-WAVENET-004 (DE-04, post-review C2): mark truncation detected; flag set
        in ``voice_meta["tts_marks_truncated"]`` so F30 DE-05 can degrade gracefully
      - INV-WAVENET-005 (post-review C8): ``audio_duration_s`` from API or None
      - INV-WAVENET-006 (DE-06, ADR-014): vendor SDK imports stay in this package
    """

    def __init__(self) -> None:
        self._client: Any = None  # lazy-init on first synthesize call

    def synthesize(self, ssml: str, voice: str) -> TTSResult:
        """Synthesize SSML to audio + timepoints; return a TTSResult."""
        client = self._get_client()
        effective_voice = voice or POC_VOICE
        request = _build_request(ssml, effective_voice)
        response = client.synthesize_speech(request=request)
        return assemble_tts_result(response, ssml=ssml, voice=effective_voice)

    def _get_client(self) -> Any:
        if self._client is None:
            self._client = build_client()
        return self._client


def _build_request(ssml: str, voice: str) -> dict[str, Any]:
    """Build the v1beta1 synthesize request dict.

    Using a plain dict (not the SDK's protobuf class) so module-load
    doesn't depend on the SDK; the v1beta1 client accepts dicts. The
    ``enable_time_pointing`` field (1 == SSML_MARK enum) gates timepoint
    return — required for F26 DE-01.
    """
    return {
        "input": {"ssml": ssml},
        "voice": {"language_code": "he-IL", "name": voice},
        "audio_config": {"audio_encoding": "MP3"},
        "enable_time_pointing": [1],  # SSML_MARK
    }
