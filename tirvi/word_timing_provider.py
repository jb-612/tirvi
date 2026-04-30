"""WordTimingProvider coordinator with auto-fallback (F03 DE-03, ADR-015).

Implements the dual-adapter pattern referenced by US-02/AC-01 and BT-012:

  1. Try ``TTSEmittedTimingAdapter``
  2. If the 3-predicate check fails (or env var ``TIRVI_TTS_MARK_RELIABILITY=low``
     is set), fall back to ``ForcedAlignmentAdapter``
  3. Emit ``timing_source`` metric on every call

The coordinator is a Protocol implementation; the two adapters land in
``tirvi/adapters/`` (F26 emits the marks-based adapter, F31 will emit the
forced-alignment adapter — out of scope for F03).

Spec: F03 DE-03. AC: US-02/AC-01. FT-anchor: FT-014. BT-anchor: BT-012.
"""

from .errors import WordTimingFallbackError  # noqa: F401  — TDD will raise this in INV-COORD-003
from .ports import WordTimingProvider
from .results import WordTimingResult


class WordTimingCoordinator(WordTimingProvider):
    """Routes timing requests across primary + fallback adapters per ADR-015.

    Invariants (named, TDD fills):
      - INV-COORD-001 (FT-014): tries TTS-marks first; falls back on schema mismatch
      - INV-COORD-002 (FT-014): the 3-predicate check is (a) non-empty marks list,
        (b) ``len(marks) == len(transcript_tokens)``, (c) marks monotonic in time
      - INV-COORD-003 (BT-012): when both adapters fail, raises
        :class:`WordTimingFallbackError` (typed, not silent)
      - INV-COORD-004 (ADR-015): records ``WordTimingResult.source`` to the
        adapter that produced the result; emits ``timing_source`` metric
      - INV-COORD-005 (ADR-015): env var ``TIRVI_TTS_MARK_RELIABILITY=low`` skips
        the TTS-marks attempt and goes straight to forced-alignment
    """

    def __init__(
        self,
        primary: WordTimingProvider,
        fallback: WordTimingProvider,
    ) -> None:
        # TODO US-02/AC-01: store primary + fallback adapters
        self._primary = primary
        self._fallback = fallback

    def get_timing(self, audio: bytes, transcript: str) -> WordTimingResult:
        # TODO INV-COORD-005: read TIRVI_TTS_MARK_RELIABILITY env var; skip primary if "low"
        # TODO INV-COORD-001: call primary; catch SchemaContractError / mismatch
        # TODO INV-COORD-002: 3-predicate check on primary result
        # TODO INV-COORD-001: on failure, call fallback
        # TODO INV-COORD-004: emit timing_source metric ("tts-marks" or "forced-alignment")
        # TODO INV-COORD-003: when both fail, raise WordTimingFallbackError
        # NOTE: the typed error import above is intentional — TDD will replace
        # this stub with logic that raises WordTimingFallbackError on dual-fail.
        raise NotImplementedError
