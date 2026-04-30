"""F10 T-05 — OCRResult v1 contract invariants.

Spec: N01/F10 DE-05. AC: US-01/AC-01. ADR-014 (contract-test-only versioning).
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestOCRv1Invariants:
    def test_us_01_ac_01_provider_must_be_string(self) -> None:
        pass

    def test_us_01_ac_01_confidence_is_float_or_none_never_zero_default(self) -> None:
        pass

    def test_us_01_ac_01_bbox_is_post_deskew_pixel_coords(self) -> None:
        pass

    def test_us_01_ac_01_lang_hint_in_known_set_or_none(self) -> None:
        pass
