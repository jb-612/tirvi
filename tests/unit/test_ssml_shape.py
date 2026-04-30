"""F23 T-05 — populate_plan_ssml end-to-end shape.

Spec: N02/F23 DE-05, DE-06. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestSSMLShape:
    def test_us_01_ac_01_returns_new_reading_plan(self) -> None:
        # Uses dataclasses.replace; original plan unchanged
        pass

    def test_us_01_ac_01_every_block_ssml_field_populated(self) -> None:
        pass

    def test_us_01_ac_01_ssml_is_valid_xml(self) -> None:
        pass
