"""T-09 — vendor-import boundary lint test.

Spec: F03 DE-06 (ADR-014 vendor-isolation).
AC: US-01/AC-01.
BT-anchors: BT-012.

Invokes ``ruff check`` as a subprocess and asserts that the
``flake8-tidy-imports.banned-api`` rule fires on synthetic vendor imports
under ``tirvi/`` (excluding ``tirvi/adapters/``).
"""

import pytest


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
