"""F32 T-01 — TTS content-hash cache always-miss POC stub."""

import pytest

from tirvi.cache.tts import get_cached_audio


def test_us_01_ac_01_returns_none_when_gate_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TIRVI_TTS_CACHE", raising=False)
    assert get_cached_audio("sha-deadbeef") is None


def test_us_01_ac_01_raises_when_gate_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TIRVI_TTS_CACHE", "1")
    with pytest.raises(NotImplementedError):
        get_cached_audio("sha-deadbeef")
