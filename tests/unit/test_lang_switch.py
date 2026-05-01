"""F24 T-01 — lang-switch policy no-op stub (deferred MVP)."""

from tirvi.ssml.lang_switch import LANG_SWITCH_ENABLED, apply_lang_policy


def test_us_01_ac_01_ft_183_disabled_returns_ssml_unchanged() -> None:
    assert LANG_SWITCH_ENABLED is False
    ssml = "<speak>hello</speak>"
    assert apply_lang_policy(ssml, [], "wavenet") == ssml
