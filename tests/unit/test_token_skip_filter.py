"""F19 T-04 — Skip filter for non-Hebrew / numeric / punct tokens.

Spec: N02/F19 DE-04. AC: US-01/AC-01. FT-anchors: FT-149.
"""

from __future__ import annotations

from tirvi.adapters.nakdan.skip_filter import should_skip_diacritization


class TestTokenSkipFilter:
    def test_us_01_ac_01_skips_non_hebrew_tokens(self) -> None:
        assert should_skip_diacritization("hello") is True
        assert should_skip_diacritization("World") is True

    def test_us_01_ac_01_skips_numeric_tokens(self) -> None:
        assert should_skip_diacritization("12345") is True
        assert should_skip_diacritization("3.14") is True

    def test_us_01_ac_01_skips_punctuation_tokens(self) -> None:
        for punct in [",", ".", "?", ";", "(", ")", "—"]:
            assert should_skip_diacritization(punct) is True

    def test_does_not_skip_hebrew_tokens(self) -> None:
        for hebrew in ["שלום", "ילד", "בית"]:
            assert should_skip_diacritization(hebrew) is False

    def test_skips_lang_hint_en_token(self) -> None:
        assert should_skip_diacritization("שלום", lang_hint="en") is True

    def test_skips_pos_num_or_punct(self) -> None:
        assert should_skip_diacritization("שלום", pos="NUM") is True
        assert should_skip_diacritization("שלום", pos="PUNCT") is True
