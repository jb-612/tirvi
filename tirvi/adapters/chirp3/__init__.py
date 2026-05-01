"""N03/F27 — Google Chirp3 HD voice TTS adapter (deferred MVP stub)."""

import os


def synthesize_chirp3(*args, **kwargs):
    if not os.getenv("TIRVI_CHIRP3"):
        raise NotImplementedError("Chirp3 adapter is deferred MVP")
    raise NotImplementedError("Chirp3 adapter implementation deferred to MVP")


__all__ = ["synthesize_chirp3"]
