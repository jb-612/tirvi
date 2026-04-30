"""F17 T-06 — DictaBERTAdapter adheres to NLPBackend contract.

Spec: N02/F17 DE-06. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestDictaBERTAdapter:
    def test_us_01_ac_01_implements_nlp_backend_runtime_check(self) -> None:
        pass

    def test_us_01_ac_01_returns_nlp_result_never_bytes(self) -> None:
        pass

    def test_us_01_ac_01_passes_assert_adapter_contract(self) -> None:
        pass
