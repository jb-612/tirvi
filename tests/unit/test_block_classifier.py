"""F11 T-03 — block heuristic classifier.

Spec: N01/F11 DE-03. AC: US-01/AC-01.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestBlockClassifier:
    def test_us_01_ac_01_heading_detected_above_modal_height(self) -> None:
        pass

    def test_us_01_ac_01_question_stem_detected_by_hebrew_prefix(self) -> None:
        # Given: a block starting with "שאלה N"
        # Then:  classifier returns "question_stem"
        pass

    def test_us_01_ac_01_paragraph_default_for_low_confidence(self) -> None:
        # Confidence < 0.6 → paragraph
        pass
