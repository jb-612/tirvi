"""F27 (N03) T-01 — Google Chirp3 adapter deferred stub."""

import pytest

from tirvi.adapters.chirp3 import synthesize_chirp3


def test_us_01_ac_01_raises_when_env_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TIRVI_CHIRP3", raising=False)
    with pytest.raises(NotImplementedError):
        synthesize_chirp3("hello", voice="he-IL-Chirp3")
