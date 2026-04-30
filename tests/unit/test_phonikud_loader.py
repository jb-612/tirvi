"""F20 T-01 — Phonikud lazy loader with fallback.

Spec: N02/F20 DE-01, ADR-022. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPhonikudLoader:
    def test_us_01_ac_01_lazy_imports_on_first_call(self) -> None:
        pass

    def test_us_01_ac_01_falls_back_to_g2p_fake_when_missing(self) -> None:
        pass
