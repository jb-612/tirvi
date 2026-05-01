"""N05/F40 T-01 — gate stub for quality-gates-ci.

Asserts the module loads cleanly, public symbols exist, and the deferred
runner raises ``NotImplementedError`` per PLAN-POC.md §Deferred.
"""

import pytest


def test_module_imports_and_exports():
    from tirvi import quality_gates

    assert hasattr(quality_gates, "GateReport")
    assert hasattr(quality_gates, "run_gates")


def test_gate_report_constructable():
    from tirvi.quality_gates import GateReport

    r = GateReport(passed=True)
    assert r.passed is True
    assert r.failures == []
    assert r.thresholds == {}


def test_run_gates_deferred_stub():
    from tirvi.quality_gates import run_gates

    with pytest.raises(NotImplementedError, match="F40"):
        run_gates("bench/thresholds.yaml")
