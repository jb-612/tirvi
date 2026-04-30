"""F26 T-03 — TTSResult assembly with audio_duration_s + word_marks.

Spec: N03/F26 DE-03. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestTTSResultAssembly:
    def test_us_01_ac_01_word_marks_parsed_from_timepoints(self) -> None:
        pass

    def test_us_01_ac_01_audio_duration_s_extracted(self) -> None:
        pass

    def test_us_01_ac_01_audio_duration_s_none_when_api_silent(self) -> None:
        # Wavenet behavior is inconsistent (post-review C8)
        pass

    def test_us_01_ac_01_provider_stamp_wavenet(self) -> None:
        pass
