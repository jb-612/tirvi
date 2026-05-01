"""F28 T-01 — Azure TTS adapter deferred stub."""

import pytest

from tirvi.adapters.azure_tts import synthesize_azure


def test_us_01_ac_01_raises_when_env_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TIRVI_AZURE_TTS", raising=False)
    with pytest.raises(NotImplementedError):
        synthesize_azure("hello", voice="he-IL-Hila")
