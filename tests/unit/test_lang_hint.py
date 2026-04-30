"""F08 T-04 — Inline lang_hint detector.

Spec: N01/F08 DE-04. AC: US-01/AC-01. FT-anchors: FT-058.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestLangHintDetector:
    def test_us_01_ac_01_ft_058_marks_hebrew_words_he(self) -> None:
        pass

    def test_us_01_ac_01_ft_058_marks_english_words_en(self) -> None:
        pass

    def test_us_01_ac_01_ft_058_unknown_script_returns_none(self) -> None:
        pass
