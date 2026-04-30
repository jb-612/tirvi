"""T-01 — package structure tests. Spec: F03 DE-01. AC: US-01/AC-01."""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPackageStructure:
    """T-01: scaffold tirvi Python package."""

    def test_us_01_ac_01_tirvi_package_imports(self) -> None:
        # Given: a fresh interpreter
        # When:  ``import tirvi`` is executed
        # Then:  the package imports without ImportError
        # And:   ``tirvi.__version__`` is a string
        pass

    def test_us_01_ac_01_public_modules_importable(self) -> None:
        # Given: the tirvi package is installed
        # When:  each public module is imported
        # Then:  ``tirvi.ports``, ``tirvi.results``, ``tirvi.fakes``, ``tirvi.contracts``
        #        all import without error
        pass

    def test_us_01_ac_01_adapters_subpackage_exists(self) -> None:
        # Given: F03 DE-06 vendor-import boundary
        # When:  ``import tirvi.adapters`` is executed
        # Then:  the subpackage exists (anchor for the ruff banned-api whitelist)
        pass
