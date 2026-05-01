"""N03/F32 — Content-hash audio cache (deferred MVP always-miss stub)."""

import os


def get_cached_audio(reading_plan_sha: str):
    if os.getenv("TIRVI_TTS_CACHE"):
        raise NotImplementedError("TTS cache backend not wired (deferred MVP)")
    return None


__all__ = ["get_cached_audio"]
