"""F08 T-05/T-06 — Optional Hough deskew preprocessor.

Spec: N01/F08 DE-05, DE-06. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-059, FT-060. BT-anchors: BT-041, BT-042, BT-043.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestDeskew:
    def test_us_01_ac_01_ft_059_deskew_disabled_by_default(self) -> None:
        pass

    def test_us_01_ac_01_ft_060_deskew_5_degree_threshold(self) -> None:
        # Skews < 5° are left alone; ≥ 5° are corrected
        pass

    def test_us_02_ac_01_bt_042_env_var_enables_deskew(self) -> None:
        pass

    def test_us_02_ac_01_bt_043_corrupt_image_raises_typed_error(self) -> None:
        pass
