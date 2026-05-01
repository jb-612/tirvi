"""N05/F41 T-01 — gate stub for mos-study.

Asserts the module loads cleanly, public symbols exist, and the deferred
runner raises ``NotImplementedError`` per PLAN-POC.md §Deferred.
"""

import pytest


def test_module_imports_and_exports():
    from tirvi import mos

    assert hasattr(mos, "MOSResult")
    assert hasattr(mos, "run_mos_study")


def test_mos_result_constructable():
    from tirvi.mos import MOSResult

    r = MOSResult(run_id="r1")
    assert r.run_id == "r1"
    assert r.mean_mos is None
    assert r.confidence_interval is None


def test_run_mos_study_deferred_stub():
    from tirvi.mos import run_mos_study

    with pytest.raises(NotImplementedError, match="F41"):
        run_mos_study([], {})
