"""F26 T-04 — mark truncation detection (post-review C2).

Spec: N03/F26 DE-04. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestMarkTruncation:
    def test_us_01_ac_01_detects_input_mark_count_vs_timepoint_count_mismatch(self) -> None:
        pass

    def test_us_01_ac_01_sets_voice_meta_tts_marks_truncated_true(self) -> None:
        pass

    def test_us_01_ac_01_no_truncation_means_flag_false(self) -> None:
        pass
