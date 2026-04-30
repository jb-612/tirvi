"""F20 T-05 — G2P skip filter for non-vocalizable tokens.

Spec: N02/F20 DE-04. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-156. BT-anchors: BT-102.
"""

from __future__ import annotations

from tirvi.adapters.phonikud.skip_filter import should_skip_g2p


class TestG2PSkipFilter:
    def test_us_01_ac_01_skips_punctuation(self) -> None:
        for punct in [",", ".", "?", ";", "(", ")", "—"]:
            assert should_skip_g2p(punct) is True

    def test_us_01_ac_01_skips_numeric_tokens(self) -> None:
        assert should_skip_g2p("12345") is True
        assert should_skip_g2p("3.14") is True

    def test_skips_non_hebrew(self) -> None:
        assert should_skip_g2p("hello") is True

    def test_does_not_skip_hebrew_words(self) -> None:
        assert should_skip_g2p("שלום") is False

    def test_skips_lang_hint_en(self) -> None:
        assert should_skip_g2p("שלום", lang_hint="en") is True

    def test_skips_pos_num_or_punct(self) -> None:
        assert should_skip_g2p("שלום", pos="NUM") is True
        assert should_skip_g2p("שלום", pos="PUNCT") is True
