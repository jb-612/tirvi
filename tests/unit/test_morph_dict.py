"""F18 T-02 — morphology dict whitelist.

Spec: N02/F18 DE-02. AC: US-01/AC-01. FT-anchors: FT-136.
"""

from __future__ import annotations

import pytest

from tirvi.nlp.errors import MorphKeyOutOfScope
from tirvi.nlp.morph import MORPH_KEYS_WHITELIST, validate_morph_features


class TestMorphDict:
    def test_us_01_ac_01_morph_keys_whitelisted(self) -> None:
        assert MORPH_KEYS_WHITELIST == frozenset(
            {"gender", "number", "person", "tense", "def", "case"}
        )

    def test_us_01_ac_01_morph_values_short_tags(self) -> None:
        # Allowed values are short UD-Hebrew tag strings
        features = {"gender": "Masc", "number": "Sing", "person": "3"}
        validated = validate_morph_features(features)
        assert validated == features
        for value in validated.values():
            assert isinstance(value, str)
            assert len(value) <= 8

    def test_unknown_key_raises_morph_key_out_of_scope(self) -> None:
        with pytest.raises(MorphKeyOutOfScope):
            validate_morph_features({"polarity": "Neg"})

    def test_empty_features_returns_empty_dict(self) -> None:
        assert validate_morph_features({}) == {}
