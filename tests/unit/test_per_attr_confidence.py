"""F17 T-04 — per-attribute confidence on NLPToken.

Spec: N02/F17 DE-04. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-128. BT-anchors: BT-083, BT-084.
"""

from __future__ import annotations

from tirvi.adapters.dictabert.inference import _decode_token


class TestPerAttrConfidence:
    def test_us_01_ac_01_pos_carries_confidence(self) -> None:
        item = {
            "token": "ילד",
            "lex": "ילד",
            "syntax": {"pos": "NOUN"},
            "confidence": 0.92,
        }
        token = _decode_token(item)
        assert token.pos == "NOUN"
        assert token.confidence == 0.92

    def test_us_01_ac_01_lemma_carries_confidence(self) -> None:
        item = {
            "token": "רץ",
            "lex": "רוץ",
            "syntax": {"pos": "VERB"},
            "confidence": 0.65,
        }
        token = _decode_token(item)
        assert token.lemma == "רוץ"
        assert token.confidence == 0.65

    def test_us_01_ac_01_confidence_none_not_zero_default(self) -> None:
        # Provider silent on confidence → None, NOT 0.0 (biz S01)
        item = {"token": "ילד", "lex": "ילד", "syntax": {"pos": "NOUN"}}
        token = _decode_token(item)
        assert token.confidence is None
        assert token.confidence != 0.0
