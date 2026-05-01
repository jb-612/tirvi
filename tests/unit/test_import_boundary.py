"""Vendor-import boundary lint tests and CI grep-gates.

T-09: F03 DE-06 (ADR-014 vendor-isolation) — ruff banned-api rule.
T-00/F18: CI grep-gate for _legacy_pick_sense isolation.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def test_legacy_pick_sense_not_imported_outside_test_disambiguate() -> None:
    """T-00/F18 grep-gate: _legacy_pick_sense must only be imported by test_disambiguate.py.

    Allows the definition in disambiguate.py; blocks any import from other callers.
    """
    import re

    root = Path(__file__).parent.parent.parent
    # Matches: `import _legacy_pick_sense` or `from ... import _legacy_pick_sense`
    pattern = re.compile(r"\bimport\b.*\b_legacy_pick_sense\b")
    violations = []
    for py_file in root.rglob("*.py"):
        if py_file.name in {"test_disambiguate.py", "disambiguate.py", "test_import_boundary.py"}:
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if pattern.search(source):
            violations.append(str(py_file.relative_to(root)))
    assert violations == [], (
        f"_legacy_pick_sense imported outside test_disambiguate.py: {violations}"
    )


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestVendorImportBoundary:
    """T-09: ruff banned-api rule blocks vendor SDKs outside ``tirvi/adapters/``."""

    def test_us_01_ac_01_ruff_blocks_google_cloud_in_tirvi_core(self, tmp_path) -> None:
        # Given: a synthetic file at tirvi/_test_vendor_import.py with
        #        ``from google.cloud import vision``
        # When:  ``ruff check tirvi/_test_vendor_import.py`` is invoked via subprocess
        # Then:  ruff exits non-zero
        # And:   the error message references TID251 / banned-api
        pass

    def test_us_01_ac_01_ruff_blocks_transformers_in_tirvi_core(self, tmp_path) -> None:
        pass

    def test_us_01_ac_01_ruff_blocks_torch_in_tirvi_core(self, tmp_path) -> None:
        pass

    def test_us_01_ac_01_ruff_blocks_huggingface_hub_in_tirvi_core(self, tmp_path) -> None:
        pass

    def test_us_01_ac_01_ruff_allows_google_cloud_in_tirvi_adapters(self, tmp_path) -> None:
        # Given: a synthetic file at tirvi/adapters/_test_vendor_import.py
        # When:  ``ruff check`` is invoked
        # Then:  ruff exits zero (banned-api whitelisted via per-file-ignores)
        pass
