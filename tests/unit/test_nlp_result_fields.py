"""F18 T-03 — NLPResult field shape.

Spec: N02/F18 DE-03. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestNLPResultFields:
    def test_us_01_ac_01_provider_field_required(self) -> None:
        pass

    def test_us_01_ac_01_tokens_list_required(self) -> None:
        pass

    def test_us_01_ac_01_token_carries_confidence(self) -> None:
        pass
