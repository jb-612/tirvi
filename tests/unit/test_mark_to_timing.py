"""F30 T-01 — mark→WordTiming projection.

Spec: N03/F30 DE-01, DE-02. AC: US-02/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestMarkToTiming:
    def test_us_02_ac_01_consumes_tts_result_word_marks(self) -> None:
        pass

    def test_us_02_ac_01_end_s_uses_next_mark_start(self) -> None:
        pass

    def test_us_02_ac_01_last_token_end_from_audio_duration_s(self) -> None:
        # Post-review C8: TTSResult.audio_duration_s
        pass

    def test_us_02_ac_01_last_token_end_falls_back_to_last_mark_plus_200ms(self) -> None:
        # When audio_duration_s is None
        pass
