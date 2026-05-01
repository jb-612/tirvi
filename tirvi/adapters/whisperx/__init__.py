"""N03/F31 — WhisperX forced-alignment fallback (deferred per ADR-015)."""


def align_with_whisperx(audio_bytes: bytes, ssml: str):
    raise NotImplementedError(
        "WhisperX fallback deferred to MVP per ADR-015"
    )


__all__ = ["align_with_whisperx"]
