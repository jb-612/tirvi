"""F26 — TTSResult assembly from a Wavenet v1beta1 SynthesizeSpeechResponse.

Spec: N03/F26 DE-03, DE-04. AC: US-01/AC-01.

``assemble_tts_result`` converts a Wavenet response into a
:class:`tirvi.results.TTSResult` shaped for F30 consumption.
``audio_duration_s`` is extracted from the response when present
(post-review C8); some Wavenet voices/regions don't surface duration
— ``None`` is the legitimate signal there.

Truncation detection (DE-04, post-review C2): when the input SSML's
``<mark>`` count differs from the response's timepoint count,
``voice_meta["tts_marks_truncated"]`` is True; F30 DE-05 reads this
flag to take the graceful-alignment path.
"""

from typing import Any

from tirvi.results import TTSResult, WordMark

PROVIDER = "wavenet"
CODEC = "mp3"


def assemble_tts_result(response: Any, *, ssml: str, voice: str) -> TTSResult:
    """Build a TTSResult from a v1beta1 SynthesizeSpeechResponse."""
    timepoints = list(response.timepoints) if response.timepoints else []
    word_marks = _build_word_marks(timepoints)
    truncated = _detect_mark_truncation(ssml, len(timepoints))
    return TTSResult(
        provider=PROVIDER,
        audio_bytes=bytes(response.audio_content),
        codec=CODEC,
        voice_meta={
            "voice": voice,
            "tts_marks_truncated": truncated,
        },
        word_marks=word_marks,
        audio_duration_s=_extract_duration_s(response),
    )


def _build_word_marks(timepoints: list[Any]) -> list[WordMark] | None:
    """Return WordMark list from response timepoints, or None when empty.

    Per F03 INV-PORT-TTS-002, ``None`` is a legitimate value — distinguishes
    "no marks emitted" (Chirp-3-HD-like) from "empty list" (degenerate).
    """
    if not timepoints:
        return None
    return [_timepoint_to_mark(tp) for tp in timepoints]


def _timepoint_to_mark(tp: Any) -> WordMark:
    """Convert a single Wavenet timepoint to a WordMark."""
    start_ms = int(round(tp.time_seconds * 1000))
    return WordMark(
        mark_id=tp.mark_name,
        start_ms=start_ms,
        end_ms=start_ms,
    )


def _detect_mark_truncation(ssml: str, timepoint_count: int) -> bool:
    """Detect Wavenet's mark-truncation behavior on Hebrew SSML (post-review C2)."""
    return _count_input_marks(ssml) != timepoint_count


def _count_input_marks(ssml: str) -> int:
    """Count ``<mark`` element openings in SSML.

    Matches both ``<mark name="..."/>`` (with attrs) and ``<mark/>``
    (bare self-close). The plain word ``mark`` in text content does NOT
    match because we require ``<`` immediately before. POC: substring
    counter; ElementTree-based count for hardening if needed.
    """
    return ssml.count("<mark ") + ssml.count("<mark/>")


def _extract_duration_s(response: Any) -> float | None:
    """Pull audio_duration_s from response; ``None`` when API didn't report it."""
    duration = getattr(response, "audio_duration", None)
    if duration is None:
        return None
    try:
        return float(duration.total_seconds())
    except AttributeError:
        return None
