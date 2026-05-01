"""N05/F43 T-01 — gate stub for ttl-automation.

Asserts the module loads cleanly, public symbols exist, and the deferred
runner raises ``NotImplementedError`` per PLAN-POC.md §Deferred.
"""

import pytest


def test_module_imports_and_exports():
    from tirvi import ttl

    assert hasattr(ttl, "TTLReport")
    assert hasattr(ttl, "apply_ttl")


def test_ttl_report_constructable():
    from tirvi.ttl import TTLReport

    r = TTLReport()
    assert r.applied_prefixes == []
    assert r.excluded_prefixes == []
    assert r.rule_active is False


def test_apply_ttl_deferred_stub():
    from tirvi.ttl import apply_ttl

    with pytest.raises(NotImplementedError, match="F43"):
        apply_ttl(["pdfs/"], {"ttl_days": 7})
