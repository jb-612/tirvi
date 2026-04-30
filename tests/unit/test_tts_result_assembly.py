"""F26 T-03 — TTSResult assembly from Wavenet response.

Spec: N03/F26 DE-03. AC: US-01/AC-01.

``assemble_tts_result(response, ssml, voice)`` builds a TTSResult from
a v1beta1 SynthesizeSpeechResponse:
  - ``audio_bytes`` from ``response.audio_content``
  - ``word_marks`` from ``response.timepoints`` (may be empty)
  - ``audio_duration_s`` from response if present, else None
    (Wavenet behavior is inconsistent — post-review C8)
  - ``voice_meta`` records voice + tts_marks_truncated flag (T-04)
  - ``provider = "wavenet"``
"""

from unittest.mock import MagicMock

from tirvi.adapters.wavenet.assembly import assemble_tts_result
from tirvi.results import TTSResult


def _response(
    *,
    audio_content: bytes = b"<mp3>",
    timepoints: list[tuple[str, float]] | None = None,
    audio_duration_s: float | None = None,
) -> MagicMock:
    r = MagicMock()
    r.audio_content = audio_content
    if timepoints is None:
        r.timepoints = []
    else:
        r.timepoints = [
            MagicMock(mark_name=name, time_seconds=t) for name, t in timepoints
        ]
    if audio_duration_s is not None:
        # Some v1beta1 versions surface this on the response; mock as attr
        r.audio_duration = MagicMock(total_seconds=lambda: audio_duration_s)
    else:
        # Simulate API silence — attribute may be missing or zero
        r.audio_duration = None
    return r


class TestAssembleTTSResult:
    def test_us_01_ac_01_returns_tts_result(self) -> None:
        out = assemble_tts_result(
            _response(timepoints=[("b1-0", 0.0)]), ssml="<speak/>", voice="he-IL-Wavenet-D"
        )
        assert isinstance(out, TTSResult)

    def test_us_01_ac_01_provider_stamp_wavenet(self) -> None:
        out = assemble_tts_result(
            _response(timepoints=[("a", 0.0)]), ssml="<speak/>", voice="he-IL-Wavenet-D"
        )
        assert out.provider == "wavenet"

    def test_us_01_ac_01_audio_bytes_from_audio_content(self) -> None:
        out = assemble_tts_result(
            _response(audio_content=b"\x00\x01\x02"),
            ssml="<speak/>",
            voice="he-IL-Wavenet-D",
        )
        assert out.audio_bytes == b"\x00\x01\x02"
        assert out.codec == "mp3"

    def test_us_01_ac_01_word_marks_parsed_from_timepoints(self) -> None:
        out = assemble_tts_result(
            _response(timepoints=[("b1-0", 0.0), ("b1-1", 0.5)]),
            ssml="<speak><mark name='b1-0'/>a<mark name='b1-1'/>b</speak>",
            voice="he-IL-Wavenet-D",
        )
        assert out.word_marks is not None
        assert len(out.word_marks) == 2
        assert out.word_marks[0].mark_id == "b1-0"
        assert out.word_marks[0].start_ms == 0
        assert out.word_marks[1].mark_id == "b1-1"
        assert out.word_marks[1].start_ms == 500

    def test_us_01_ac_01_word_marks_none_when_timepoints_empty(self) -> None:
        # Mark-less providers (Chirp-3-HD-like) — F03 INV-PORT-TTS-002
        out = assemble_tts_result(
            _response(timepoints=[]), ssml="<speak/>", voice="he-IL-Wavenet-D"
        )
        assert out.word_marks is None

    def test_us_01_ac_01_audio_duration_s_extracted_when_present(self) -> None:
        out = assemble_tts_result(
            _response(timepoints=[("a", 0.0)], audio_duration_s=2.5),
            ssml="<speak/>",
            voice="he-IL-Wavenet-D",
        )
        assert out.audio_duration_s == 2.5

    def test_us_01_ac_01_audio_duration_s_none_when_api_silent(self) -> None:
        # Wavenet inconsistency — post-review C8
        out = assemble_tts_result(
            _response(timepoints=[("a", 0.0)], audio_duration_s=None),
            ssml="<speak/>",
            voice="he-IL-Wavenet-D",
        )
        assert out.audio_duration_s is None

    def test_us_01_ac_01_voice_recorded_in_voice_meta(self) -> None:
        out = assemble_tts_result(
            _response(timepoints=[("a", 0.0)]),
            ssml="<speak/>",
            voice="he-IL-Wavenet-D",
        )
        assert out.voice_meta["voice"] == "he-IL-Wavenet-D"

    def test_us_01_ac_01_tts_marks_truncated_default_false(self) -> None:
        out = assemble_tts_result(
            _response(timepoints=[("a", 0.0)]),
            ssml="<speak><mark name='a'/></speak>",
            voice="he-IL-Wavenet-D",
        )
        assert out.voice_meta["tts_marks_truncated"] is False
