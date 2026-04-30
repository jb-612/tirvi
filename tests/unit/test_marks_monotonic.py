"""F30 — marks monotonicity invariant.

Spec: N03/F30 DE-04. AC: US-02/AC-01.
FT-anchors: FT-215. BT-anchors: BT-146.

``assert_marks_monotonic`` raises :class:`TimingInvariantError` on the
first non-monotonic pair (catches Wavenet API regression). Also wires
into ``TTSEmittedTimingAdapter.get_timing`` so a non-monotonic
TTSResult fails fast at adapter time, not later in the player.
"""

import pytest

from tirvi.adapters.tts_marks.adapter import TTSEmittedTimingAdapter
from tirvi.adapters.tts_marks.invariants import (
    TimingInvariantError,
    assert_marks_monotonic,
)
from tirvi.results import TTSResult, WordMark


def _marks(*pairs: tuple[str, int]) -> list[WordMark]:
    return [WordMark(mark_id=m, start_ms=ms, end_ms=ms) for m, ms in pairs]


class TestAssertMarksMonotonic:
    def test_us_02_ac_01_ft_215_monotonic_marks_pass(self) -> None:
        # No exception raised on strictly increasing start_ms
        assert_marks_monotonic(_marks(("a", 0), ("b", 100), ("c", 200)))

    def test_us_02_ac_01_ft_215_equal_start_ms_passes(self) -> None:
        # Adjacent equal timestamps allowed (Wavenet sometimes reports this
        # for tightly-coupled morphemes); only strict regression raises.
        assert_marks_monotonic(_marks(("a", 100), ("b", 100), ("c", 200)))

    def test_us_02_ac_01_ft_215_empty_list_passes(self) -> None:
        assert_marks_monotonic([])

    def test_us_02_ac_01_ft_215_single_mark_passes(self) -> None:
        assert_marks_monotonic(_marks(("a", 100)))

    def test_us_02_ac_01_bt_146_non_monotonic_raises(self) -> None:
        with pytest.raises(TimingInvariantError):
            assert_marks_monotonic(_marks(("a", 100), ("b", 50)))

    def test_us_02_ac_01_bt_146_error_message_reports_indices(self) -> None:
        with pytest.raises(TimingInvariantError, match=r"\b1\b"):
            assert_marks_monotonic(_marks(("a", 100), ("b", 50)))


class TestAdapterIntegration:
    def test_us_02_ac_01_bt_146_get_timing_raises_on_non_monotonic(self) -> None:
        bad = TTSResult(
            provider="wavenet-fake",
            audio_bytes=b"",
            codec="mp3",
            voice_meta={},
            word_marks=_marks(("a", 200), ("b", 100)),  # regression
            audio_duration_s=1.0,
        )
        adapter = TTSEmittedTimingAdapter(bad)
        with pytest.raises(TimingInvariantError):
            adapter.get_timing(b"", "x y")
