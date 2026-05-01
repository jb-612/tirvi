"""Tests for ProgressReporter protocol, StageTiming, PipelineReport, and NoOpProgressReporter."""

from __future__ import annotations

import dataclasses
import importlib

import pytest


# ---------------------------------------------------------------------------
# StageTiming tests
# ---------------------------------------------------------------------------


def test_stage_timing_is_frozen_dataclass() -> None:
    """StageTiming mutation must raise FrozenInstanceError."""
    from tirvi.progress import StageTiming

    st = StageTiming(name="ocr", elapsed_s=1.23, metric_label="42 words")
    with pytest.raises(dataclasses.FrozenInstanceError):
        st.name = "mutated"  # type: ignore[misc]


def test_stage_timing_value_equality() -> None:
    """Two StageTiming instances with identical fields must compare equal."""
    from tirvi.progress import StageTiming

    a = StageTiming(name="ocr", elapsed_s=1.23, metric_label="42 words")
    b = StageTiming(name="ocr", elapsed_s=1.23, metric_label="42 words")
    assert a == b


def test_stage_timing_errored_defaults_false() -> None:
    """StageTiming.errored must default to False when not supplied."""
    from tirvi.progress import StageTiming

    st = StageTiming(name="nakdan", elapsed_s=0.5, metric_label="10 tokens")
    assert st.errored is False


# ---------------------------------------------------------------------------
# PipelineReport tests
# ---------------------------------------------------------------------------


def test_pipeline_report_is_frozen_dataclass() -> None:
    """PipelineReport mutation must raise FrozenInstanceError."""
    from tirvi.progress import PipelineReport, StageTiming

    stage = StageTiming(name="ocr", elapsed_s=1.0, metric_label="1 word")
    report = PipelineReport(stages=(stage,))
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.stages = ()  # type: ignore[misc]


def test_pipeline_report_empty_stages() -> None:
    """PipelineReport(stages=()) must be valid (no error on construction)."""
    from tirvi.progress import PipelineReport

    report = PipelineReport(stages=())
    assert report.stages == ()


def test_pipeline_report_stages_is_tuple() -> None:
    """PipelineReport.stages must be a tuple."""
    from tirvi.progress import PipelineReport, StageTiming

    stage = StageTiming(name="tts", elapsed_s=2.5, metric_label="512 KB")
    report = PipelineReport(stages=(stage,))
    assert isinstance(report.stages, tuple)


# ---------------------------------------------------------------------------
# ProgressReporter protocol tests
# ---------------------------------------------------------------------------


def test_progress_reporter_protocol_structural() -> None:
    """A class with all five required methods satisfies ProgressReporter structurally."""
    from tirvi.progress import ProgressReporter

    class ConcreteReporter:
        def stage_started(self, name: str, total_tokens: int | None = None) -> None:
            pass

        def stage_completed(self, name: str, elapsed_s: float, metric_label: str) -> None:
            pass

        def stage_error(self, name: str, error_label: str) -> None:
            pass

        def token_tick(self) -> None:
            pass

        def summarize(self) -> None:
            pass

    # runtime_checkable Protocol: isinstance must pass
    assert isinstance(ConcreteReporter(), ProgressReporter)


def test_progress_reporter_method_signatures() -> None:
    """ProgressReporter must expose the five expected method names."""
    from tirvi.progress import ProgressReporter

    for method_name in (
        "stage_started",
        "stage_completed",
        "stage_error",
        "token_tick",
        "summarize",
    ):
        assert hasattr(ProgressReporter, method_name), (
            f"ProgressReporter missing method: {method_name}"
        )


# ---------------------------------------------------------------------------
# T-02 RED phase: NoOpProgressReporter
# ---------------------------------------------------------------------------


def test_noop_satisfies_protocol() -> None:
    """NoOpProgressReporter must satisfy the ProgressReporter runtime-checkable Protocol."""
    from tirvi.progress import NoOpProgressReporter, ProgressReporter

    assert isinstance(NoOpProgressReporter(), ProgressReporter)


def test_noop_stage_started_silent() -> None:
    """NoOpProgressReporter.stage_started() must return None without raising."""
    from tirvi.progress import NoOpProgressReporter

    noop = NoOpProgressReporter()
    result = noop.stage_started("OCR")
    assert result is None


def test_noop_stage_completed_silent() -> None:
    """NoOpProgressReporter.stage_completed() must return None without raising."""
    from tirvi.progress import NoOpProgressReporter

    noop = NoOpProgressReporter()
    result = noop.stage_completed("OCR", 1.2, "5 words")
    assert result is None


def test_noop_stage_error_silent() -> None:
    """NoOpProgressReporter.stage_error() must return None without raising."""
    from tirvi.progress import NoOpProgressReporter

    noop = NoOpProgressReporter()
    result = noop.stage_error("OCR", "failed")
    assert result is None


def test_noop_token_tick_silent() -> None:
    """NoOpProgressReporter.token_tick() must return None without raising."""
    from tirvi.progress import NoOpProgressReporter

    noop = NoOpProgressReporter()
    result = noop.token_tick()
    assert result is None


def test_noop_summarize_silent() -> None:
    """NoOpProgressReporter.summarize() must return None without raising."""
    from tirvi.progress import NoOpProgressReporter

    noop = NoOpProgressReporter()
    result = noop.summarize()
    assert result is None


def test_noop_does_not_import_rich() -> None:
    """Importing tirvi.progress must NOT cause rich to appear in sys.modules."""
    import sys

    # Remove tirvi.progress from sys.modules to force a fresh import, then
    # check that rich has not been pulled in as a side effect.
    sys.modules.pop("tirvi.progress", None)

    # Also evict rich in case a prior test already loaded it, so this test
    # is deterministic regardless of import order.
    rich_keys = [k for k in sys.modules if k == "rich" or k.startswith("rich.")]
    for key in rich_keys:
        sys.modules.pop(key, None)

    import tirvi.progress  # noqa: F401 — side-effect import under test

    assert "rich" not in sys.modules, (
        "tirvi.progress must not import rich; it was found in sys.modules after import"
    )
