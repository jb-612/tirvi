"""N05/F39 DE-01/DE-02 — benchmark runner (deferred post-POC stub).

Drives the full OCR -> NLP -> TTS pipeline against held-out reference pages
and records WER + MOS-proxy quality metrics. Real implementation deferred
per PLAN-POC.md §Deferred.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BenchResult:
    """Aggregated benchmark output. Spec: N05/F39 DE-02.

    Per-page metrics + summary written as JSON to GCS at
    ``bench/{run_id}/results.json`` when the runner is wired.
    """

    run_id: str
    per_page: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


def run_bench(
    pipeline_fn: Callable[[Any], Any],
    inputs: Iterable[Any],
) -> BenchResult:
    """Run pipeline against reference inputs and return aggregated metrics.

    Deferred post-POC: raises ``NotImplementedError``. TDD will fill the
    GCS read, pipeline drive, WER diff, and JSON serialisation.
    """
    raise NotImplementedError("F39 tirvi-bench-v0 runner — deferred post-POC")
