"""F18 T-02 — morph_features whitelist (POC numbering).

Spec: N02/F18 DE-02. AC: US-01/AC-01. FT-anchors: FT-136.

POC scope intentionally narrow: only the six UD-Hebrew morphology
attributes the demo PDF exercises are accepted. Anything outside the
whitelist raises :class:`MorphKeyOutOfScope` so the v0.1 work can lift
the constraint deliberately.
"""

from __future__ import annotations

from .errors import MorphKeyOutOfScope

MORPH_KEYS_WHITELIST: frozenset[str] = frozenset(
    {"gender", "number", "person", "tense", "def", "case"}
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
