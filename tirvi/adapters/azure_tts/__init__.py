"""N03/F28 — Azure Cognitive Services TTS adapter (deferred MVP stub)."""

import os


def synthesize_azure(*args, **kwargs):
    if not os.getenv("TIRVI_AZURE_TTS"):
        raise NotImplementedError("Azure TTS adapter is deferred MVP")
    raise NotImplementedError("Azure TTS adapter implementation deferred to MVP")


__all__ = ["synthesize_azure"]
