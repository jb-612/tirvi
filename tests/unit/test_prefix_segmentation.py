"""F17 T-03 — Hebrew prefix segmentation (NLPToken.prefix_segments).

Spec: N02/F17 DE-03. AC: US-01/AC-01. FT-anchors: FT-126.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from tirvi.adapters.dictabert.inference import _decode_token, analyze
from tirvi.results import NLPToken


class TestPrefixSegmentation:
    def test_us_01_ac_01_segments_hebrew_prefixes(self) -> None:
        # "בבית" (in-house) decomposes into ("ב", "בית")
        item = {
            "token": "בבית",
            "lex": "בית",
            "syntax": {"pos": "NOUN"},
            "prefix_segments": ["ב", "בית"],
        }
        token = _decode_token(item)
        assert token.text == "בבית"
        assert token.prefix_segments == ("ב", "בית")

    def test_us_01_ac_01_no_prefix_returns_none(self) -> None:
        item = {"token": "ילד", "lex": "ילד", "syntax": {"pos": "NOUN"}}
        token = _decode_token(item)
        assert token.prefix_segments is None

    def test_prefix_segments_preserved_through_analyze(self) -> None:
        canned = [NLPToken(text="בבית", pos="NOUN", prefix_segments=("ב", "בית"))]
        with patch(
            "tirvi.adapters.dictabert.inference.load_model",
            return_value=(MagicMock(), MagicMock()),
        ), patch(
            "tirvi.adapters.dictabert.inference._run_joint_predict",
            return_value=canned,
        ):
            result = analyze("בבית", lang="he")
        assert result.tokens[0].prefix_segments == ("ב", "בית")
