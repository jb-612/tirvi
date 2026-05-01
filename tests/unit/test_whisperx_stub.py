"""F31 T-01 — WhisperX forced-alignment fallback deferred stub (ADR-015)."""

import pytest

from tirvi.adapters.whisperx import align_with_whisperx


def test_us_01_ac_01_always_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        align_with_whisperx(b"", "<speak/>")
