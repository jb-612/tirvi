"""F19 T-01 — Nakdan model loader.

Spec: N02/F19 DE-01, ADR-021. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestNakdanLoader:
    def test_us_01_ac_01_loader_is_lru_cached(self) -> None:
        pass

    def test_us_01_ac_01_releases_cuda_cache_between_stages(self) -> None:
        pass
