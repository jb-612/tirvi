"""F18 T-05 — assert_nlp_result_v1 contract harness.

Spec: N02/F18 DE-05. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestNLPv1Invariants:
    def test_us_01_ac_01_pos_whitelist_enforced(self) -> None:
        pass

    def test_us_01_ac_01_morph_keys_whitelisted(self) -> None:
        pass

    def test_us_01_ac_01_ambiguous_consistent_with_margin(self) -> None:
        pass

    def test_us_01_ac_01_confidence_never_zero_default(self) -> None:
        pass
