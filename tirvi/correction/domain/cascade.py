"""CorrectionCascade aggregate — transient per-page (biz F48-R1-3).

Spec: F48 DE-05.
BO: BO49 CorrectionCascade.

Holds the in-flight cascade state for a single page: stage decisions,
emitted events, the locked CascadeMode, and an LLM-call counter.

Strict scaffold rule: NO BUSINESS LOGIC. All mutator bodies raise
NotImplementedError with the AC + task ref so TDD fills them in.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..value_objects import CascadeMode, CorrectionVerdict
from .events import (
    CascadeModeDegraded,
    CorrectionApplied,
    CorrectionRejected,
    LLMCallCapReached,
)


@dataclass
class CorrectionCascade:
    """Transient per-page aggregate.

    Lifecycle:
      - Constructed at the start of every page run by
        ``CorrectionCascadeService.run_page``.
      - Mutated as each token's ``ICascadeStage.evaluate(...)`` returns.
      - Discarded after the page's ``CorrectionLog`` row is written.

    Invariants (named, TDD fills):
      - INV-CCS-001 (DE-05): token-in / token-out — every recorded
        verdict yields exactly one output token (or none).
      - INV-CCS-005 (DE-07): mode is fixed once locked; later locks
        with a different name raise ``CascadeConfigInvalid``.
      - INV-CCS-003 (DE-06): on ``run_page`` completion, every applied
        correction has a corresponding ``CorrectionLogEntry`` written.

    AC: F48-S01/AC-01, F48-S02/AC-03, F48-S03/AC-01, F48-S04/AC-01.
    """

    page_index: int
    sha: str
    _mode: CascadeMode | None = None
    _stage_decisions: list[CorrectionVerdict] = field(default_factory=list)
    _applied: list[CorrectionApplied] = field(default_factory=list)
    _rejected: list[CorrectionRejected] = field(default_factory=list)
    _mode_events: list[CascadeModeDegraded] = field(default_factory=list)
    _llm_calls_made: int = 0
    _llm_cap: int = 10
    _cap_events: list[LLMCallCapReached] = field(default_factory=list)

    # ---- mode lifecycle (DE-07, INV-CCS-005) ------------------------------

    def lock_mode(self, mode: CascadeMode) -> None:
        """Lock the per-page cascade mode at run_page entry.

        TODO INV-CCS-005 (T-07): if ``self._mode is not None`` and
        ``mode.name != self._mode.name``, raise ``CascadeConfigInvalid``.
        Otherwise set ``self._mode = mode`` and (if mode.name != "full")
        emit a ``CascadeModeDegraded`` event into ``_mode_events``.
        """
        raise NotImplementedError("AC-F48-S06/AC-01 / INV-CCS-005 — TDD T-07 fills")

    @property
    def mode(self) -> CascadeMode | None:
        return self._mode

    # ---- stage recording (DE-05) ------------------------------------------

    def record_decision(self, verdict: CorrectionVerdict) -> None:
        """Record a stage's verdict on the current token.

        TODO INV-CCS-001 (T-05): apply ``TokenInTokenOutPolicy.check``
        before appending.
        TODO T-05: append to ``self._stage_decisions``.
        TODO T-05: if verdict in {"auto_apply", "apply"}, emit
        ``CorrectionApplied``; if verdict.reason indicates rejection
        (anti-hallucination / parse-failure / user-override), emit
        ``CorrectionRejected``.
        """
        raise NotImplementedError("AC-F48-S01/AC-01 / INV-CCS-001 — TDD T-05 fills")

    @property
    def stage_decisions(self) -> tuple[CorrectionVerdict, ...]:
        return tuple(self._stage_decisions)

    # ---- LLM-call cap (BT-F-05) -------------------------------------------

    def configure_llm_cap(self, cap: int) -> None:
        """Set the per-page cap (default 10)."""
        # TODO T-04a: assert cap > 0; set self._llm_cap = cap.
        raise NotImplementedError("AC-F48-S03/AC-02 / BT-F-05 — TDD T-04a fills")

    def note_llm_call(self) -> None:
        """Increment the LLM-call counter; emit cap event when reached.

        TODO BT-F-05 (T-04a): increment ``self._llm_calls_made``; if equal
        to ``self._llm_cap`` emit ``LLMCallCapReached`` into
        ``_cap_events``.
        """
        raise NotImplementedError("AC-F48-S03/AC-02 / BT-F-05 — TDD T-04a fills")

    def llm_cap_reached(self) -> bool:
        """Return whether the per-page LLM-call cap has been reached."""
        # TODO T-04a: return self._llm_calls_made >= self._llm_cap.
        raise NotImplementedError("AC-F48-S03/AC-02 / BT-F-05 — TDD T-04a fills")

    # ---- event drainage (DE-05) -------------------------------------------

    def drain_events(self) -> tuple[
        tuple[CorrectionApplied, ...],
        tuple[CorrectionRejected, ...],
        tuple[CascadeModeDegraded, ...],
        tuple[LLMCallCapReached, ...],
    ]:
        """Return all events accumulated this page; clear internal buffers.

        TODO T-05: snapshot all four event lists, clear them, return tuples.
        Service publishes the snapshot to its EventListener bus.
        """
        raise NotImplementedError("AC-F48-S01/AC-01 — TDD T-05 fills")


__all__ = ["CorrectionCascade"]
