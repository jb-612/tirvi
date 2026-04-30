"""F17 T-03 — Hebrew prefix segmentation (NLPToken.prefix_segments).

Spec: N02/F17 DE-03. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPrefixSegmentation:
    def test_us_01_ac_01_segments_hebrew_prefixes(self) -> None:
        # e.g., "בבית" → ["ב", "בית"]
        pass

    def test_us_01_ac_01_no_prefix_returns_none(self) -> None:
        pass
