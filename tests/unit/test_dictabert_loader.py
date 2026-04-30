"""F17 T-01 — DictaBERT module-level LRU loader.

Spec: N02/F17 DE-01, ADR-020. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestDictaBERTLoader:
    def test_us_01_ac_01_loader_is_lru_cached(self) -> None:
        # Two calls return the same model instance
        pass

    def test_us_01_ac_01_loader_lazy_first_call(self) -> None:
        pass
