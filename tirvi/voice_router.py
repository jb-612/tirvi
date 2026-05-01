"""N03/F29 — Voice routing policy (deferred MVP single-voice POC stub)."""

import os


def route_voice(block, config) -> str:
    if os.getenv("TIRVI_VOICE_ROUTING"):
        raise NotImplementedError("Multi-voice routing policy deferred to MVP")
    return "wavenet"


__all__ = ["route_voice"]
