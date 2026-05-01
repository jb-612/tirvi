"""N05/F40 DE-01/DE-02 — pytest-driven CI quality gates (deferred post-POC stub).

Reads latest F39 benchmark results from GCS and asserts WER / MOS-proxy
metrics are within thresholds defined in ``bench/thresholds.yaml``. Real
gate logic deferred per PLAN-POC.md §Deferred.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GateReport:
    """Result of a quality-gate run. Spec: N05/F40 DE-01."""

    passed: bool
    failures: list[dict[str, Any]] = field(default_factory=list)
    thresholds: dict[str, Any] = field(default_factory=dict)


def run_gates(config_path: str | Path) -> GateReport:
    """Evaluate gates against the latest benchmark results.

    Deferred post-POC: raises ``NotImplementedError``. TDD will fill the
    GCS fetch, threshold parse, and per-page assertion logic.
    """
    raise NotImplementedError("F40 quality-gates-ci runner — deferred post-POC")
