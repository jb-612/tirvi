"""F18 T-02 — morphology dict whitelist (Wave-2: UD TitleCase).

Spec: N02/F18 DE-02. AC: US-01/AC-01. FT-anchors: FT-136.

Wave-2 replaces the Wave-1 lowercase whitelist with UD v2 canonical
TitleCase keys per https://universaldependencies.org/u/feat/index.html.
R2 finding R-3 (Critical): morph-key UD spelling mismatch.
"""

from __future__ import annotations

import pytest

from tirvi.nlp.errors import MorphKeyOutOfScope
from tirvi.nlp.morph import MORPH_KEYS_WHITELIST, validate_morph_features


class TestMorphDict:
    def test_us_01_ac_01_morph_keys_whitelisted_ud_titlecase(self) -> None:
        assert MORPH_KEYS_WHITELIST == frozenset(
            {"Gender", "Number", "Person", "Tense", "Definite", "Case", "VerbForm"}
        )

    def test_us_01_ac_01_morph_values_ud_hebrew_tags(self) -> None:
        features = {"Gender": "Masc", "Number": "Sing", "Person": "3"}
        validated = validate_morph_features(features)
        assert validated == features
        for value in validated.values():
            assert isinstance(value, str)

    def test_unknown_key_raises_morph_key_out_of_scope(self) -> None:
        with pytest.raises(MorphKeyOutOfScope):
            validate_morph_features({"Polarity": "Neg"})

    def test_lowercase_key_raises_morph_key_out_of_scope_r3_regression(self) -> None:
        """R-3 regression: wave-1 lowercase keys must now be rejected."""
        with pytest.raises(MorphKeyOutOfScope):
            validate_morph_features({"gender": "Masc"})

    def test_verbform_key_accepted(self) -> None:
        assert validate_morph_features({"VerbForm": "Part"}) == {"VerbForm": "Part"}

    def test_definite_key_accepted(self) -> None:
        assert validate_morph_features({"Definite": "Def"}) == {"Definite": "Def"}

    def test_empty_features_returns_empty_dict(self) -> None:
        assert validate_morph_features({}) == {}
