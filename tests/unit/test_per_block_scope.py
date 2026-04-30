"""F30 T-03 — per-block timing scope (no cross-block leakage).

Spec: N03/F30 DE-03. AC: US-02/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPerBlockScope:
    def test_us_02_ac_01_timings_scoped_to_one_block(self) -> None:
        pass

    def test_us_02_ac_01_provider_stamp_tts_marks(self) -> None:
        pass

    def test_us_02_ac_01_source_field_tts_marks(self) -> None:
        pass
