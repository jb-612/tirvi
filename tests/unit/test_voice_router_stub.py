"""F29 T-01 — voice routing policy single-voice POC stub."""

import pytest

from tirvi.voice_router import route_voice


def test_us_01_ac_01_constant_wavenet_when_gate_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TIRVI_VOICE_ROUTING", raising=False)
    assert route_voice(object(), {}) == "wavenet"


def test_us_01_ac_01_raises_when_routing_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TIRVI_VOICE_ROUTING", "1")
    with pytest.raises(NotImplementedError):
        route_voice(object(), {})
