"""F30 T-04 — TTSEmittedTimingAdapter graceful path (post-review C2).

Spec: N03/F30 DE-05. AC: US-02/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestTTSMarksAdapterGracefulPath:
    def test_us_02_ac_01_truncated_marks_aligns_by_min_count(self) -> None:
        # voice_meta["tts_marks_truncated"] = True →
        # align by min(len(marks), len(transcript)); log warning
        pass

    def test_us_02_ac_01_truncated_emits_synthetic_tail_with_end_none(self) -> None:
        pass

    def test_us_02_ac_01_genuine_mismatch_raises_mark_count_mismatch(self) -> None:
        # When truncation NOT signalled and counts differ
        pass

    def test_us_02_ac_01_no_truncation_emits_full_timings(self) -> None:
        pass
