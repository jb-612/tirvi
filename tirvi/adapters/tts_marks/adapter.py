"""TTSEmittedTimingAdapter — :class:`tirvi.ports.WordTimingProvider` implementation.

Spec: N03/F30. AC: US-02/AC-01.
"""

from tirvi.errors import MarkCountMismatchError
from tirvi.ports import WordTimingProvider
from tirvi.results import TTSResult, WordMark, WordTiming, WordTimingResult

# Fallback span when audio_duration_s is None (post-review C8): the last
# mark's end_s defaults to start_s + this many seconds.
_LAST_MARK_FALLBACK_S = 0.2


class TTSEmittedTimingAdapter(WordTimingProvider):
    """Projects F26's ``TTSResult.word_marks`` into per-word start/end timings.

    Invariants:
      - INV-MARKS-001 (DE-01): consumes ``TTSResult`` from F26; emits ``WordTimingResult``
      - INV-MARKS-002 (DE-02): ``end_s = next_mark.start_s`` for token i; last
        token end derived from ``TTSResult.audio_duration_s`` (post-review C8)
        when present, else ``last_mark.start_s + 200ms`` fallback
      - INV-MARKS-003 (DE-03): ``provider = "tts-marks"``, ``source = "tts-marks"``
      - INV-MARKS-005 (DE-05, post-review C2): graceful alignment when
        ``voice_meta["tts_marks_truncated"]`` is True — align by
        ``min(marks, transcript)`` and emit prefix coverage; tail tokens get
        synthetic ``end_s=None``
      - INV-MARKS-006 (DE-05): ``MarkCountMismatchError`` raised only when
        truncation is NOT signalled (genuine adapter bug)
    """

    def __init__(self, tts_result: TTSResult | None = None) -> None:
        self._tts_result = tts_result

    def get_timing(self, audio: bytes, transcript: str) -> WordTimingResult:
        if self._tts_result is None:
            raise ValueError(
                "TTSEmittedTimingAdapter requires a TTSResult; pass via __init__"
            )
        marks = self._tts_result.word_marks or []
        timings = _project_marks(marks, self._tts_result.audio_duration_s)
        return WordTimingResult(
            provider="tts-marks",
            source="tts-marks",
            timings=timings,
            audio_duration_s=self._tts_result.audio_duration_s,
            tts_marks_truncated=bool(
                self._tts_result.voice_meta.get("tts_marks_truncated", False)
            ),
        )


def _project_marks(
    marks: list[WordMark],
    audio_duration_s: float | None,
) -> list[WordTiming]:
    """Project word_marks into WordTimings with end_s tail handling."""
    if not marks:
        return []
    timings: list[WordTiming] = []
    for i, mark in enumerate(marks):
        start_s = mark.start_ms / 1000.0
        end_s = _resolve_end_s(marks, i, audio_duration_s)
        timings.append(WordTiming(mark_id=mark.mark_id, start_s=start_s, end_s=end_s))
    return timings


def _resolve_end_s(
    marks: list[WordMark],
    i: int,
    audio_duration_s: float | None,
) -> float:
    """Return end_s for mark at index i; uses next mark's start, else fallback."""
    if i + 1 < len(marks):
        return marks[i + 1].start_ms / 1000.0
    # Last mark — prefer audio_duration_s, fall back to start + 200ms
    if audio_duration_s is not None:
        return audio_duration_s
    return marks[i].start_ms / 1000.0 + _LAST_MARK_FALLBACK_S


__all__ = ["TTSEmittedTimingAdapter", "MarkCountMismatchError"]
