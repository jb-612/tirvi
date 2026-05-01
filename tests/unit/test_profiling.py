"""N05/F42 T-01 — gate stub for latency-cost-profiling.

Asserts the module loads cleanly, public symbols exist, and the deferred
runner raises ``NotImplementedError`` per PLAN-POC.md §Deferred.
"""

import pytest


def test_module_imports_and_exports():
    from tirvi import profiling

    assert hasattr(profiling, "ProfilingReport")
    assert hasattr(profiling, "profile_pipeline")


def test_profiling_report_constructable():
    from tirvi.profiling import ProfilingReport

    r = ProfilingReport(n_runs=3)
    assert r.n_runs == 3
    assert r.per_stage_ms == {}
    assert r.cost_usd == {}


def test_profile_pipeline_deferred_stub():
    from tirvi.profiling import profile_pipeline

    with pytest.raises(NotImplementedError, match="F42"):
        profile_pipeline(lambda: None, n_runs=1)
