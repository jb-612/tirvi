"""Progress reporting protocol and value objects for the pipeline."""

from __future__ import annotations

import dataclasses
import datetime
import logging as _logging
import sys
from typing import Any, Protocol, runtime_checkable

_log = _logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class StageTiming:
    """Immutable record of a single pipeline stage's timing and outcome."""

    name: str
    elapsed_s: float | None
    metric_label: str
    errored: bool = False


@dataclasses.dataclass(frozen=True)
class PipelineReport:
    """Immutable summary of all stage timings for a pipeline run."""

    stages: tuple[StageTiming, ...]


@runtime_checkable
class ProgressReporter(Protocol):
    """Protocol for reporting pipeline progress."""

    def stage_started(self, name: str, total_tokens: int | None = None) -> None:
        ...

    def stage_completed(self, name: str, elapsed_s: float, metric_label: str) -> None:
        ...

    def stage_error(self, name: str, error_label: str) -> None:
        ...

    def token_tick(self) -> None:
        ...

    def summarize(self) -> None:
        ...


class NoOpProgressReporter:
    def stage_started(self, name: str, total_tokens: int | None = None) -> None:
        return None

    def stage_completed(self, name: str, elapsed_s: float, metric_label: str) -> None:
        return None

    def stage_error(self, name: str, error_label: str) -> None:
        return None

    def token_tick(self) -> None:
        return None

    def summarize(self) -> None:
        return None


class ProgressReporterEventBridge:
    """Bridges EventListener calls to ProgressReporter.token_tick().

    Wraps a ProgressReporter and implements the EventListener protocol
    from tirvi.correction.service, so a reporter can be registered as
    a cascade listener without coupling the two protocols.
    """

    def __init__(self, reporter: ProgressReporter) -> None:
        self._reporter = reporter
        self.llm_call_count: int = 0

    def on_correction_applied(self, event: Any) -> None:
        self._reporter.token_tick()
        if getattr(event, "chosen_by_stage", None) == "llm_reviewer":
            self.llm_call_count += 1

    def on_correction_rejected(self, event: Any) -> None:
        self._reporter.token_tick()

    def on_cascade_mode_degraded(self, event: Any) -> None:
        pass  # No-op — degraded mode is noted but not surfaced in progress

    def on_llm_call_cap_reached(self, event: Any) -> None:
        pass  # No-op — cap signal


class RichProgressReporter:
    """Rich terminal progress reporter for the pipeline.

    Not thread-safe — designed for single-threaded pipeline use only.
    TTY path uses rich Live + Progress; non-TTY path uses logging.INFO.
    """

    def __init__(self) -> None:
        self._is_tty = sys.stdout.isatty()
        self._stages: list[tuple[str, float | None, str]] = []
        self._live: Any = None
        self._progress: Any = None
        self._rich_tasks: dict[str, Any] = {}
        if self._is_tty:
            try:
                from rich.live import Live  # type: ignore[import]
                from rich.progress import (  # type: ignore[import]
                    BarColumn,
                    Progress,
                    SpinnerColumn,
                    TextColumn,
                    TimeElapsedColumn,
                )

                self._progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[bold]{task.description}"),
                    TimeElapsedColumn(),
                    TextColumn("{task.fields[metric]}"),
                )
                self._live = Live(self._progress, refresh_per_second=10)
                self._live.start()
            except ImportError:
                self._is_tty = False  # fall back to log path

    def stage_started(self, name: str, total_tokens: int | None = None) -> None:
        if self._is_tty and self._progress is not None:
            task_id = self._progress.add_task(name, total=total_tokens or 100, metric="")
            self._rich_tasks[name] = task_id
        else:
            ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            _log.info("[%s] %s started", ts, name)

    def stage_completed(self, name: str, elapsed_s: float, metric_label: str) -> None:
        self._stages.append((name, elapsed_s, metric_label))
        if self._is_tty and self._progress is not None and name in self._rich_tasks:
            self._progress.update(self._rich_tasks[name], completed=100, metric=metric_label)
        else:
            ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            _log.info("[%s] %s done elapsed=%.2fs %s", ts, name, elapsed_s, metric_label)

    def stage_error(self, name: str, error_label: str) -> None:
        self._stages.append((name, None, f"ERROR: {error_label}"))
        if not self._is_tty:
            ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            _log.info("[%s] %s error: %s", ts, name, error_label)

    def token_tick(self) -> None:
        pass  # TTY progress-bar advance not required in T-05 non-TTY scope

    def summarize(self) -> None:
        sorted_stages = sorted(
            self._stages, key=lambda s: (s[1] is None, -(s[1] or 0.0))
        )
        if self._is_tty and self._live is not None:
            self._live.stop()
            self._render_rich_summary(sorted_stages)
        else:
            self._log_plain_summary(sorted_stages)

    def _render_rich_summary(
        self, sorted_stages: list[tuple[str, float | None, str]]
    ) -> None:
        try:
            from rich.console import Console  # type: ignore[import]
            from rich.table import Table  # type: ignore[import]

            table = Table(title="Pipeline Summary")
            table.add_column("Stage")
            table.add_column("Elapsed (s)", justify="right")
            table.add_column("Metric")
            total = 0.0
            for name, elapsed, metric in sorted_stages:
                e_str = f"{elapsed:.2f}" if elapsed is not None else "—"
                table.add_row(name, e_str, metric)
                if elapsed is not None:
                    total += elapsed
            table.add_row("Total", f"{total:.2f}", "")
            Console().print(table)
        except ImportError:
            self._log_plain_summary(sorted_stages)

    def _log_plain_summary(
        self, sorted_stages: list[tuple[str, float | None, str]]
    ) -> None:
        total = 0.0
        for name, elapsed, metric in sorted_stages:
            e_str = f"{elapsed:.2f}" if elapsed is not None else "—"
            _log.info("%s\t%s\t%s", name, e_str, metric)
            if elapsed is not None:
                total += elapsed
        _log.info("Total\t%.2f\t", total)
