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
from datetime import datetime

from ..errors import CascadeConfigInvalid, CascadeInvariantViolation
from ..value_objects import CascadeMode, CorrectionVerdict
from .events import (
    CascadeModeDegraded,
    CorrectionApplied,
    CorrectionRejected,
    LLMCallCapReached,
)

_REJECTION_REASONS = {"anti_hallucination_reject", "user_override", "llm_parse_failure"}
_REJECTION_MAP = {
    "anti_hallucination_reject": "anti_hallucination",
    "user_override": "user_override",
    "llm_parse_failure": "parse_failure",
}


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
        if self._mode is not None and mode.name != self._mode.name:
            raise CascadeConfigInvalid(
                f"mid-page mode flip rejected: {self._mode.name!r} → {mode.name!r}"
            )
        self._mode = mode
        if mode.name != "full":
            self._mode_events.append(CascadeModeDegraded(
                page_index=self.page_index, mode=mode, occurred_at=datetime.utcnow(),
            ))

    @property
    def mode(self) -> CascadeMode | None:
        return self._mode

    # ---- stage recording (DE-05) ------------------------------------------

    def record_decision(self, verdict: CorrectionVerdict) -> None:
        self._check_token_shape(verdict)
        self._stage_decisions.append(verdict)
        if verdict.verdict in ("auto_apply", "apply"):
            self._applied.append(self._make_applied(verdict))
        elif verdict.reason in _REJECTION_REASONS:
            self._rejected.append(self._make_rejected(verdict))

    def _check_token_shape(self, verdict: CorrectionVerdict) -> None:
        c = verdict.corrected_or_none
        if c is None:
            return
        if len(c.split()) != 1:
            raise CascadeInvariantViolation(f"INV-CCS-001: '{c}' is not a single token")

    def _make_applied(self, verdict: CorrectionVerdict) -> CorrectionApplied:
        return CorrectionApplied(
            page_index=self.page_index,
            original=verdict.original,
            corrected=verdict.corrected_or_none or verdict.original,
            chosen_by_stage=verdict.stage,
            score=verdict.score,
            sentence_hash="",
            occurred_at=datetime.utcnow(),
        )

    def _make_rejected(self, verdict: CorrectionVerdict) -> CorrectionRejected:
        reason = verdict.reason or ""
        return CorrectionRejected(
            page_index=self.page_index,
            original=verdict.original,
            proposed=verdict.corrected_or_none,
            rejected_by=_REJECTION_MAP.get(reason, reason),
            sentence_hash="",
            reason=reason,
            occurred_at=datetime.utcnow(),
        )

    @property
    def stage_decisions(self) -> tuple[CorrectionVerdict, ...]:
        return tuple(self._stage_decisions)

    # ---- LLM-call cap (BT-F-05) -------------------------------------------

    def configure_llm_cap(self, cap: int) -> None:
        self._llm_cap = cap

    def note_llm_call(self) -> None:
        self._llm_calls_made += 1
        if self._llm_calls_made >= self._llm_cap:
            self._cap_events.append(LLMCallCapReached(
                page_index=self.page_index,
                calls_made=self._llm_calls_made,
                cap=self._llm_cap,
                occurred_at=datetime.utcnow(),
            ))

    def llm_cap_reached(self) -> bool:
        return self._llm_calls_made >= self._llm_cap

    # ---- event drainage (DE-05) -------------------------------------------

    def drain_events(self) -> tuple[
        tuple[CorrectionApplied, ...],
        tuple[CorrectionRejected, ...],
        tuple[CascadeModeDegraded, ...],
        tuple[LLMCallCapReached, ...],
    ]:
        applied = tuple(self._applied)
        rejected = tuple(self._rejected)
        mode_events = tuple(self._mode_events)
        cap_events = tuple(self._cap_events)
        self._applied.clear()
        self._rejected.clear()
        self._mode_events.clear()
        self._cap_events.clear()
        return applied, rejected, mode_events, cap_events


__all__ = ["CorrectionCascade"]
