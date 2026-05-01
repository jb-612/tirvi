"""F18 T-02 — morph_features whitelist (Wave-2: UD v2 TitleCase).

Spec: N02/F18 DE-02. AC: US-01/AC-01. FT-anchors: FT-136.

Wave-2 fixes R-3 (Critical): keys must use UD v2 canonical TitleCase
per https://universaldependencies.org/u/feat/index.html.
"""

from __future__ import annotations

from .errors import MorphKeyOutOfScope

MORPH_KEYS_WHITELIST: frozenset[str] = frozenset(
    {"Gender", "Number", "Person", "Tense", "Definite", "Case", "VerbForm"}
)


def validate_morph_features(features: dict[str, str]) -> dict[str, str]:
    """Return ``features`` unchanged after asserting every key is whitelisted.

    Raises :class:`MorphKeyOutOfScope` listing every offending key on first
    failure.
    """
    unknown = set(features) - MORPH_KEYS_WHITELIST
    if unknown:
        raise MorphKeyOutOfScope(
            f"morph_features keys not in POC whitelist: {sorted(unknown)}"
        )
    return features
