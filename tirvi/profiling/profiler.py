"""N05/F42 DE-01/DE-02 — pipeline latency + cost profiler (deferred post-POC stub).

Wraps OCR -> NLP -> TTS stages in a timing context manager and maps
billable units to USD via ``prices.yaml``; writes ``bench/{run_id}/cost.json``
when implemented. Deferred per PLAN-POC.md §Deferred.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProfilingReport:
    """Profiling output. Spec: N05/F42 DE-01/DE-02."""

    n_runs: int
    per_stage_ms: dict[str, list[float]] = field(default_factory=dict)
    cost_usd: dict[str, float] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)


def profile_pipeline(
    pipeline_fn: Callable[..., Any],
    n_runs: int,
) -> ProfilingReport:
    """Run pipeline n_runs times, capturing per-stage latency + cost.

    Deferred post-POC: raises ``NotImplementedError``. TDD will fill the
    timer context manager, billing-unit aggregation, and JSON write.
    """
    raise NotImplementedError("F42 latency-cost-profiling — deferred post-POC")
