"""F20 T-05 — Token-skip filter for the G2P stage.

Spec: N02/F20 DE-04. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-156. BT-anchors: BT-102.

Mirrors the F19 token-skip predicate: phonikud has nothing useful to say
about English glyphs, digit-only tokens, or pure punctuation. Skipped
tokens emit ``confidence=None`` per biz S01 (None ≠ 0.0).
"""

from __future__ import annotations

from tirvi.adapters.nakdan.skip_filter import should_skip_diacritization


def should_skip_g2p(
    text: str,
    lang_hint: str | None = None,
    pos: str | None = None,
) -> bool:
    """Return True when phonikud should be bypassed for this token."""
    return should_skip_diacritization(text, lang_hint=lang_hint, pos=pos)
