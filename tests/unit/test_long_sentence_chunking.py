"""F17 T-05 — long-sentence chunking (model context window).

Spec: N02/F17 DE-05. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestLongSentenceChunking:
    def test_us_01_ac_01_chunks_at_punctuation(self) -> None:
        pass

    def test_us_01_ac_01_preserves_token_boundaries_across_chunks(self) -> None:
        pass
