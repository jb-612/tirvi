"""F19 T-05 — NFC→NFD nikud normalization.

Spec: N02/F19 DE-05. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestNikudNormalize:
    def test_us_01_ac_01_nfc_input_normalized_to_nfd(self) -> None:
        pass

    def test_us_01_ac_01_already_nfd_unchanged(self) -> None:
        pass

    def test_us_01_ac_01_g2p_stability_after_normalize(self) -> None:
        pass
