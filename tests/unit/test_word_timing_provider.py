"""T-05 — WordTimingCoordinator tests.

Spec: F03 DE-03 (ADR-015 fallback).
AC: US-02/AC-01.
FT-anchors: FT-014.
BT-anchors: BT-012.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestThreePredicateCheck:
    """T-05: the 3-predicate check decides primary→fallback (INV-COORD-002)."""

    def test_us_02_ac_01_ft_014_empty_marks_list_triggers_fallback(self) -> None:
        # Given: a primary adapter that returns WordTimingResult.timings == []
        # When:  coordinator.get_timing is called
        # Then:  the fallback adapter is invoked
        # And:   result.source == "forced-alignment"
        pass

    def test_us_02_ac_01_ft_014_count_mismatch_triggers_fallback(self) -> None:
        # Given: a primary adapter where len(marks) != len(transcript_tokens)
        # And:   the upstream voice_meta does NOT signal tts_marks_truncated
        # When:  coordinator.get_timing is called
        # Then:  the fallback adapter is invoked
        pass

    def test_us_02_ac_01_ft_014_non_monotonic_marks_triggers_fallback(self) -> None:
        # Given: a primary adapter that returns marks where t[i+1] < t[i]
        # When:  coordinator.get_timing is called
        # Then:  the fallback adapter is invoked
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestEnvVarOptOut:
    """T-05: ``TIRVI_TTS_MARK_RELIABILITY=low`` skips the primary attempt
    (INV-COORD-005)."""

    def test_us_02_ac_01_env_var_low_skips_primary(self) -> None:
        # Given: TIRVI_TTS_MARK_RELIABILITY=low in environment
        # When:  coordinator.get_timing is called
        # Then:  the primary adapter is NOT invoked
        # And:   the fallback adapter IS invoked
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestBothAdaptersFail:
    """T-05: BT-012 — when both adapters fail, raise typed error
    (INV-COORD-003)."""

    def test_us_02_ac_01_bt_012_both_fail_raises_word_timing_fallback_error(self) -> None:
        # Given: a primary that returns invalid marks
        # And:   a fallback that raises an internal error
        # When:  coordinator.get_timing is called
        # Then:  WordTimingFallbackError is raised (not silent)
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestSourceFieldRecording:
    """T-05: ADR-015 — coordinator records which adapter produced the result
    (INV-COORD-004)."""

    def test_us_02_ac_01_ft_014_primary_success_records_source_tts_marks(self) -> None:
        pass

    def test_us_02_ac_01_ft_014_fallback_success_records_source_forced_alignment(self) -> None:
        pass

    def test_us_02_ac_01_timing_source_metric_emitted_on_every_call(self) -> None:
        # Given: a metrics sink registered on the coordinator
        # When:  get_timing is called (success or fallback)
        # Then:  the timing_source metric is incremented exactly once
        pass
