"""F30 — TTSEmittedTimingAdapter graceful truncation + count-match.

Spec: N03/F30 DE-05. AC: US-02/AC-01.
FT-anchors: FT-214, FT-216, FT-217. BT-anchors: BT-147, BT-148.

Two paths when ``len(word_marks) != len(transcript_tokens)``:
  - voice_meta["tts_marks_truncated"] is truthy (Hebrew Wavenet
    truncation, post-review C2): align by min count; emit prefix
    timings + synthetic tail tokens with end_s=None
  - flag NOT signalled: raise MarkCountMismatchError (genuine bug)
"""

import pytest

from tirvi.adapters.tts_marks.adapter import TTSEmittedTimingAdapter
from tirvi.errors import MarkCountMismatchError
from tirvi.results import TTSResult, WordMark


def _tts(*marks: tuple[str, int], truncated: bool = False) -> TTSResult:
    return TTSResult(
        provider="wavenet-fake",
        audio_bytes=b"",
        codec="mp3",
        voice_meta={
            "voice": "he-IL-Wavenet-D",
            "tts_marks_truncated": truncated,
        },
        word_marks=[WordMark(mark_id=m, start_ms=ms, end_ms=ms) for m, ms in marks],
        audio_duration_s=1.0,
    )


class TestTTSMarksAdapterGracefulPath:
    def test_us_02_ac_01_no_count_mismatch_passes(self) -> None:
        out = TTSEmittedTimingAdapter(_tts(("a", 0), ("b", 500))).get_timing(
            b"", "x y"
        )
        assert len(out.timings) == 2

    def test_us_02_ac_01_truncated_aligns_by_min_count(self) -> None:
        # 2 marks, 4 transcript tokens, truncation signalled →
        # emit 2 prefix timings + 2 synthetic tail tokens
        out = TTSEmittedTimingAdapter(
            _tts(("a", 0), ("b", 500), truncated=True),
        ).get_timing(b"", "w x y z")
        # Total timings count matches transcript token count
        assert len(out.timings) == 4
        # First two come from real marks
        assert out.timings[0].mark_id == "a"
        assert out.timings[1].mark_id == "b"

    def test_us_02_ac_01_truncated_synthetic_tail_has_end_s_none(self) -> None:
        out = TTSEmittedTimingAdapter(
            _tts(("a", 0), ("b", 500), truncated=True),
        ).get_timing(b"", "w x y z")
        # Last two tokens are synthetic tail
        assert out.timings[2].end_s is None
        assert out.timings[3].end_s is None
        # Synthetic mark_ids are positional placeholders
        assert out.timings[2].mark_id.startswith("tail-")
        assert out.timings[3].mark_id.startswith("tail-")

    def test_us_02_ac_01_truncated_flag_propagates_to_result(self) -> None:
        out = TTSEmittedTimingAdapter(
            _tts(("a", 0), truncated=True),
        ).get_timing(b"", "x y")
        assert out.tts_marks_truncated is True

    def test_us_02_ac_01_genuine_mismatch_raises(self) -> None:
        # 1 mark, 3 transcript tokens, truncation NOT signalled → raise
        with pytest.raises(MarkCountMismatchError):
            TTSEmittedTimingAdapter(_tts(("a", 0), truncated=False)).get_timing(
                b"", "x y z"
            )

    def test_us_02_ac_01_extra_marks_genuine_mismatch_raises(self) -> None:
        # 3 marks, 1 transcript token, truncation NOT signalled → raise
        with pytest.raises(MarkCountMismatchError):
            TTSEmittedTimingAdapter(
                _tts(("a", 0), ("b", 100), ("c", 200), truncated=False)
            ).get_timing(b"", "single")

    def test_us_02_ac_01_no_truncation_no_synthetic_tail(self) -> None:
        # Counts match, truncated=False → no synthetic tail; clean prefix
        out = TTSEmittedTimingAdapter(
            _tts(("a", 0), ("b", 500), truncated=False)
        ).get_timing(b"", "x y")
        assert len(out.timings) == 2
        assert all(t.end_s is not None for t in out.timings)

    def test_us_02_ac_01_empty_transcript_no_marks_passes(self) -> None:
        # Both empty — degenerate but legal
        out = TTSEmittedTimingAdapter(_tts(truncated=False)).get_timing(b"", "")
        assert out.timings == []
