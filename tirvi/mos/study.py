"""N05/F41 DE-01/DE-02 — MOS listening study (deferred post-POC stub).

Exports TTS sample clips with rating sheets, ingests rater CSV, and
aggregates per-voice and per-page MOS (ITU-T P.800 5-point scale) to
GCS ``bench/{run_id}/mos.json``. Real implementation deferred per
PLAN-POC.md §Deferred.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MOSResult:
    """MOS aggregation result. Spec: N05/F41 DE-02."""

    run_id: str
    mean_mos: float | None = None
    confidence_interval: tuple[float, float] | None = None
    per_voice: dict[str, Any] = field(default_factory=dict)
    per_page: dict[str, Any] = field(default_factory=dict)


def run_mos_study(
    audio_paths: Iterable[str | Path],
    config: dict[str, Any],
) -> MOSResult:
    """Run a MOS listening study and return aggregated MOS scores.

    Deferred post-POC: raises ``NotImplementedError``. TDD will fill clip
    sampling, rating-form export, ratings ingestion, and CI computation.
    """
    raise NotImplementedError("F41 mos-study runner — deferred post-POC")
