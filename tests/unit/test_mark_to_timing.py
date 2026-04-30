"""F30 — WordMark → WordTiming projection.

Spec: N03/F30 DE-01, DE-02. AC: US-02/AC-01. FT-anchors: FT-213.

The projection: each mark[i].end_s = mark[i+1].start_s; the LAST
mark's end_s is derived from TTSResult.audio_duration_s (post-review
C8) when present, else last_mark.start_s + 200ms fallback.
"""

import pytest

from tirvi.adapters.tts_marks.adapter import TTSEmittedTimingAdapter
from tirvi.results import TTSResult, WordMark, WordTimingResult


def _tts(
    *marks: tuple[str, int],
    audio_duration_s: float | None = None,
    truncated: bool = False,
) -> TTSResult:
    return TTSResult(
        provider="wavenet-fake",
        audio_bytes=b"",
        codec="mp3",
        voice_meta={"voice": "he-IL-Wavenet-D", "tts_marks_truncated": truncated},
        word_marks=[WordMark(mark_id=m, start_ms=ms, end_ms=ms) for m, ms in marks],
        audio_duration_s=audio_duration_s,
    )


class TestMarkToTiming:
    def test_us_02_ac_01_ft_213_returns_word_timing_result(self) -> None:
        adapter = TTSEmittedTimingAdapter(
            _tts(("b1-0", 0), ("b1-1", 500), audio_duration_s=1.0)
        )
        out = adapter.get_timing(b"", "שלום עולם")
        assert isinstance(out, WordTimingResult)
        assert out.provider == "tts-marks"
        assert out.source == "tts-marks"

    def test_us_02_ac_01_ft_213_consumes_tts_result_word_marks(self) -> None:
        adapter = TTSEmittedTimingAdapter(
            _tts(("b1-0", 0), ("b1-1", 500), audio_duration_s=1.0)
        )
        out = adapter.get_timing(b"", "שלום עולם")
        assert len(out.timings) == 2
        assert out.timings[0].mark_id == "b1-0"
        assert out.timings[1].mark_id == "b1-1"

    def test_us_02_ac_01_ft_213_end_s_uses_next_mark_start(self) -> None:
        adapter = TTSEmittedTimingAdapter(
            _tts(("a", 0), ("b", 500), ("c", 1200), audio_duration_s=2.0)
        )
        out = adapter.get_timing(b"", "x y z")
        # ms → seconds conversion
        assert out.timings[0].start_s == 0.0
        assert out.timings[0].end_s == 0.5
        assert out.timings[1].start_s == 0.5
        assert out.timings[1].end_s == 1.2

    def test_us_02_ac_01_ft_213_last_token_end_from_audio_duration_s(self) -> None:
        # Post-review C8: TTSResult.audio_duration_s wins for last token's end.
        adapter = TTSEmittedTimingAdapter(
            _tts(("a", 0), ("b", 500), audio_duration_s=2.5)
        )
        out = adapter.get_timing(b"", "x y")
        assert out.timings[-1].end_s == 2.5

    def test_us_02_ac_01_ft_213_last_token_end_falls_back_to_last_mark_plus_200ms(
        self,
    ) -> None:
        # When audio_duration_s is None, last token's end = last_mark.start + 0.2s
        adapter = TTSEmittedTimingAdapter(
            _tts(("a", 0), ("b", 500), audio_duration_s=None)
        )
        out = adapter.get_timing(b"", "x y")
        assert out.timings[-1].end_s == pytest.approx(0.7)

    def test_us_02_ac_01_audio_duration_s_propagated_to_result(self) -> None:
        adapter = TTSEmittedTimingAdapter(_tts(("a", 0), audio_duration_s=1.5))
        out = adapter.get_timing(b"", "x")
        assert out.audio_duration_s == 1.5

    def test_us_02_ac_01_empty_marks_emits_empty_timings(self) -> None:
        adapter = TTSEmittedTimingAdapter(_tts(audio_duration_s=0.0))
        out = adapter.get_timing(b"", "")
        assert out.timings == []
