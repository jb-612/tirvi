"""F30 T-01 + T-05 — TTSEmittedTimingAdapter (class + graceful truncation).

Spec: N03/F30 DE-01 (T-01) + DE-05 (T-05). AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-213, FT-214, FT-216, FT-217. BT-anchors: BT-147, BT-148.

T-01 — class-level conformance:
  - TTSEmittedTimingAdapter implements the WordTimingProvider port
  - emits WordTimingResult with provider == "tts-marks"

T-05 — graceful truncation, two paths when ``len(word_marks) != len(transcript_tokens)``:
  - voice_meta["tts_marks_truncated"] is truthy (Hebrew Wavenet
    truncation, post-review C2): align by min count; emit prefix
    timings + synthetic tail tokens with end_s=None
  - flag NOT signalled: raise MarkCountMismatchError (genuine bug)
"""

import pytest

from tirvi.adapters.tts_marks.adapter import TTSEmittedTimingAdapter
from tirvi.errors import MarkCountMismatchError
from tirvi.ports import WordTimingProvider
from tirvi.results import TTSResult, WordMark, WordTimingResult


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


class TestTTSMarksAdapterPortConformance:
    """F30 T-01 (DE-01, FT-213): adapter class shape + provider tag."""

    def test_us_01_ac_01_ft_213_implements_word_timing_provider_port(self) -> None:
        # INV-PORT-WT-001 / DE-01: must satisfy the WordTimingProvider Protocol
        # (runtime_checkable) so the coordinator can hold it without a TYPE
        # branch. Instance-level isinstance check exercises the runtime port.
        adapter = TTSEmittedTimingAdapter(_tts(("a", 0)))
        assert isinstance(adapter, WordTimingProvider)

    def test_us_01_ac_01_ft_213_get_timing_returns_word_timing_result(self) -> None:
        # DE-01: surface returns WordTimingResult, never raw bytes (BT-009)
        out = TTSEmittedTimingAdapter(_tts(("a", 0))).get_timing(b"", "x")
        assert isinstance(out, WordTimingResult)

    def test_us_01_ac_01_ft_213_provider_is_tts_marks(self) -> None:
        # INV-MARKS-003 (DE-03): provider tag is the literal "tts-marks"
        # so downstream consumers can route on adapter origin (ADR-015).
        out = TTSEmittedTimingAdapter(_tts(("a", 0))).get_timing(b"", "x")
        assert out.provider == "tts-marks"
        assert out.source == "tts-marks"


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


class TestTTSMarksAdapterTruncationWarning:
    """F30 T-06 (DE-05): truncated path logs a warning with counts."""

    def test_us_01_ac_01_truncated_logs_warning_with_counts(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        with caplog.at_level(logging.WARNING, logger="tirvi.adapters.tts_marks"):
            TTSEmittedTimingAdapter(
                _tts(("a", 0), ("b", 500), truncated=True),
            ).get_timing(b"", "w x y z")
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        assert warnings, "expected a WARNING log for truncated alignment"
        msg = warnings[0].getMessage()
        assert "2" in msg and "4" in msg

    def test_us_01_ac_01_no_warning_when_counts_match(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import logging

        with caplog.at_level(logging.WARNING, logger="tirvi.adapters.tts_marks"):
            TTSEmittedTimingAdapter(
                _tts(("a", 0), ("b", 500), truncated=True),
            ).get_timing(b"", "x y")
        assert not [r for r in caplog.records if r.levelno == logging.WARNING]
