"""F25 T-01 — content reading templates no-op stub (deferred MVP)."""

from tirvi.templates import TEMPLATES_ENABLED, apply_content_template


def test_us_01_ac_01_disabled_returns_block_identity() -> None:
    assert TEMPLATES_ENABLED is False
    block = object()
    assert apply_content_template(block) is block
