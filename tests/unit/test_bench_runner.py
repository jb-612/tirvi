"""N05/F39 T-01 — gate stub for tirvi-bench-v0.

Asserts the module loads cleanly, public symbols exist, and the deferred
runner raises ``NotImplementedError`` per PLAN-POC.md §Deferred.
"""

import pytest


def test_module_imports_and_exports():
    from tirvi import bench

    assert hasattr(bench, "BenchResult")
    assert hasattr(bench, "run_bench")


def test_bench_result_constructable():
    from tirvi.bench import BenchResult

    r = BenchResult(run_id="r1")
    assert r.run_id == "r1"
    assert r.per_page == []
    assert r.summary == {}


def test_run_bench_deferred_stub():
    from tirvi.bench import run_bench

    with pytest.raises(NotImplementedError, match="F39"):
        run_bench(lambda x: x, [])
