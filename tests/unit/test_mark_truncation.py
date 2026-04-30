"""F26 T-04 — mark truncation detection (post-review C2).

Spec: N03/F26 DE-04. AC: US-01/AC-01.

Hebrew Wavenet sometimes returns fewer timepoints than the SSML's
``<mark>`` count — the post-review C2 graceful path. F26 detects the
mismatch and sets ``voice_meta["tts_marks_truncated"]``; F30 DE-05
already consumes the flag and aligns by ``min(marks, transcript)``.
"""

from unittest.mock import MagicMock

from tirvi.adapters.wavenet.assembly import assemble_tts_result


def _response(timepoints: list[tuple[str, float]]) -> MagicMock:
    r = MagicMock()
    r.audio_content = b"<mp3>"
    r.timepoints = [
        MagicMock(mark_name=name, time_seconds=t) for name, t in timepoints
    ]
    r.audio_duration = None
    return r


class TestMarkTruncation:
    def test_us_01_ac_01_no_truncation_means_flag_false(self) -> None:
        # 3 marks in SSML, 3 timepoints in response — counts match
        ssml = '<speak><mark name="a"/><mark name="b"/><mark name="c"/></speak>'
        out = assemble_tts_result(
            _response([("a", 0.0), ("b", 0.5), ("c", 1.0)]),
            ssml=ssml,
            voice="he-IL-Wavenet-D",
        )
        assert out.voice_meta["tts_marks_truncated"] is False

    def test_us_01_ac_01_detects_fewer_timepoints_than_input_marks(self) -> None:
        # 3 marks in SSML, only 2 timepoints returned (Hebrew Wavenet truncation)
        ssml = '<speak><mark name="a"/><mark name="b"/><mark name="c"/></speak>'
        out = assemble_tts_result(
            _response([("a", 0.0), ("b", 0.5)]),
            ssml=ssml,
            voice="he-IL-Wavenet-D",
        )
        assert out.voice_meta["tts_marks_truncated"] is True

    def test_us_01_ac_01_detects_more_timepoints_than_input_marks(self) -> None:
        # Defensive: more timepoints than input marks (shouldn't happen but
        # any inequality is suspicious)
        ssml = '<speak><mark name="a"/></speak>'
        out = assemble_tts_result(
            _response([("a", 0.0), ("ghost", 0.5)]),
            ssml=ssml,
            voice="he-IL-Wavenet-D",
        )
        assert out.voice_meta["tts_marks_truncated"] is True

    def test_us_01_ac_01_zero_marks_zero_timepoints_not_truncated(self) -> None:
        # Edge case: SSML has no marks; response has no timepoints
        out = assemble_tts_result(
            _response([]), ssml="<speak>שלום</speak>", voice="he-IL-Wavenet-D"
        )
        assert out.voice_meta["tts_marks_truncated"] is False

    def test_us_01_ac_01_ssml_mark_count_uses_full_tag_match(self) -> None:
        # The substring count must match "<mark " exactly so the word "mark"
        # appearing as text content doesn't inflate the count
        ssml = (
            '<speak>The word <mark name="a"/>"mark" appears here'
            ' but only one <mark/> opens</speak>'
        )
        # 2 actual <mark elements; if we count "mark" as substring we'd get more
        # 2 timepoints → match → flag should be False
        out = assemble_tts_result(
            _response([("a", 0.0), ("b", 0.5)]),
            ssml=ssml,
            voice="he-IL-Wavenet-D",
        )
        assert out.voice_meta["tts_marks_truncated"] is False
