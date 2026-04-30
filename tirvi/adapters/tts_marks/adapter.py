"""TTSEmittedTimingAdapter — :class:`tirvi.ports.WordTimingProvider` implementation.

Spec: N03/F30. AC: US-02/AC-01.
"""

from tirvi.ports import WordTimingProvider
from tirvi.results import TTSResult, WordTimingResult


class TTSEmittedTimingAdapter(WordTimingProvider):
    """Projects F26's ``TTSResult.word_marks`` into per-word start/end timings.

    Invariants (named, TDD fills):
      - INV-MARKS-001 (DE-01): consumes ``TTSResult`` from F26; emits ``WordTimingResult``
      - INV-MARKS-002 (DE-02): ``end_s = next_mark.start_s`` for token i; last token
        end derived from ``TTSResult.audio_duration_s`` (post-review C8) when present,
        else ``last_mark.start_s + 200ms`` fallback
      - INV-MARKS-003 (DE-03): ``provider = "tts-marks"``, ``source = "tts-marks"``
      - INV-MARKS-004 (DE-04): monotonicity invariant; rejects non-monotonic marks
      - INV-MARKS-005 (DE-05, post-review C2): graceful alignment when
        ``tts_marks_truncated`` is signalled — align by ``min(marks, transcript)``,
        log warning, emit prefix coverage + synthetic ``end_s=None`` for tail tokens
      - INV-MARKS-006 (DE-05): ``MarkCountMismatchError`` raised only when truncation
        is NOT signalled (genuine adapter bug)
    """

    def __init__(self, tts_result: TTSResult | None = None) -> None:
        # TODO US-02/AC-01: cache TTSResult (or accept later via get_timing's audio bytes)
        self._tts_result = tts_result

    def get_timing(self, audio: bytes, transcript: str) -> WordTimingResult:
        # TODO INV-MARKS-001..002 (T-02): project word_marks into WordTimings
        # TODO INV-MARKS-005 (T-04, post-review C2): inspect voice_meta.tts_marks_truncated
        # TODO INV-MARKS-006: raise MarkCountMismatchError only on genuine mismatch
        raise NotImplementedError
