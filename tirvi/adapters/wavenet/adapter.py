"""WavenetTTSAdapter — :class:`tirvi.ports.TTSBackend` implementation.

Spec: N03/F26. AC: US-01/AC-01.
"""

from tirvi.ports import TTSBackend
from tirvi.results import TTSResult


class WavenetTTSAdapter(TTSBackend):
    """Google Wavenet TTS adapter (he-IL voices) using v1beta1 ``timepoints``.

    Invariants (named, TDD fills):
      - INV-WAVENET-001 (DE-01): uses v1beta1 client to receive ``timepoints``
      - INV-WAVENET-002 (DE-02): voice = ``he-IL-Wavenet-D`` for POC
      - INV-WAVENET-003 (DE-03): timepoints parsed into :class:`tirvi.results.WordMark`
      - INV-WAVENET-004 (DE-04, post-review C2): mark truncation detected; flag set
        in ``voice_meta["tts_marks_truncated"]`` so F30 DE-05 can degrade gracefully
      - INV-WAVENET-005 (post-review C8): ``audio_duration_s`` from API or None
      - INV-WAVENET-006 (DE-06, ADR-014): vendor SDK imports stay in this module
    """

    def __init__(self, voice: str = "he-IL-Wavenet-D") -> None:
        # TODO US-01/AC-01: lazy-init google.cloud.texttospeech client (v1beta1)
        self._voice = voice

    def synthesize(self, ssml: str, voice: str) -> TTSResult:
        # TODO INV-WAVENET-001: client.synthesize_speech(ssml, voice, enable_time_pointing=True)
        # TODO INV-WAVENET-003: parse timepoints into list[WordMark]
        # TODO INV-WAVENET-004: detect input <mark> vs timepoint count mismatch;
        #                        set voice_meta["tts_marks_truncated"] flag
        # TODO INV-WAVENET-005: extract audio_duration_s from response (None when absent)
        raise NotImplementedError
