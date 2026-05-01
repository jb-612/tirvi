"""F24 — Inline language-switch policy (deferred MVP stub).

Spec: N02/F24 DE-01. AC: US-01/AC-01. FT-183 deferred.
"""

LANG_SWITCH_ENABLED = False


def apply_lang_policy(ssml: str, lang_spans: list, voice_profile: str) -> str:
    """No-op until LANG_SWITCH_ENABLED is True (deferred MVP)."""
    if LANG_SWITCH_ENABLED:
        raise NotImplementedError("F24 lang-switch policy deferred to MVP")
    return ssml


__all__ = ["LANG_SWITCH_ENABLED", "apply_lang_policy"]
