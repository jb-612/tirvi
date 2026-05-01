"""CorrectionCascadeService — orchestrator for the F48 cascade (DE-05).

Spec: F48 DE-05.
AC: F48-S01/AC-01, F48-S02/AC-03, F48-S03/AC-01.
T-05.

Conditionally walks DE-02 → DE-03 → DE-04 over each token in a page.
Holds a transient ``CorrectionCascade`` aggregate per page (biz F48-R1-3).
Emits ``CorrectionApplied`` / ``CorrectionRejected`` /
``CascadeModeDegraded`` / ``LLMCallCapReached`` to registered listeners
via an in-process pub-sub Protocol (no broker, ADR-033).

Strict scaffold rule: NO BUSINESS LOGIC. ``run_page`` body raises
``NotImplementedError`` — TDD T-05 fills.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol, Sequence, runtime_checkable

from .domain.cascade import CorrectionCascade
from .domain.events import (
    CascadeModeDegraded,
    CorrectionApplied,
    CorrectionRejected,
    LLMCallCapReached,
)
from .ports import (
    FeedbackReadPort,
    ICascadeStage,
)
from .value_objects import CascadeMode, CorrectionVerdict, SentenceContext


@runtime_checkable
class EventListener(Protocol):
    """In-process pub-sub Protocol (DE-05).

    Listeners are passed via ``CorrectionCascadeService(listeners=[...])``.
    No broker, no infra (ADR-033).
    """

    def on_correction_applied(
        self, event: CorrectionApplied
    ) -> None:  # pragma: no cover — Protocol
        ...

    def on_correction_rejected(
        self, event: CorrectionRejected
    ) -> None:  # pragma: no cover — Protocol
        ...

    def on_cascade_mode_degraded(
        self, event: CascadeModeDegraded
    ) -> None:  # pragma: no cover — Protocol
        ...

    def on_llm_call_cap_reached(
        self, event: LLMCallCapReached
    ) -> None:  # pragma: no cover — Protocol
        ...


@dataclass(frozen=True)
class PageCorrections:
    """Result of a single page's cascade run (T-05).

    Carries the corrected token sequence (token-in==token-out per
    INV-CCS-001), the per-token stage decisions, and a snapshot of
    events for downstream log writers.
    """

    page_index: int
    sha: str
    original_tokens: tuple[str, ...]
    corrected_tokens: tuple[str, ...]
    stage_decisions: tuple[CorrectionVerdict, ...]
    mode: CascadeMode
    applied: tuple[CorrectionApplied, ...]
    rejected: tuple[CorrectionRejected, ...]
    mode_events: tuple[CascadeModeDegraded, ...]
    cap_events: tuple[LLMCallCapReached, ...]


@dataclass
class CorrectionCascadeService:
    """Orchestrator for the F48 correction cascade (DE-05).

    Wiring:
      - ``nakdan_gate``  : DE-02 first-stage word-list filter
      - ``mlm_scorer``   : DE-03 confusion-table + MLM ranker
      - ``llm_reviewer`` : DE-04 local Gemma reviewer (optional in no_llm mode)
      - ``feedback``     : DE-08 user-rejection read at init (BT-211)
      - ``listeners``    : in-process event subscribers (no broker)

    Lifecycle (per page):
      1. Construct fresh ``CorrectionCascade`` aggregate.
      2. ``lock_mode(mode)`` from health probe (DE-07 / T-07).
      3. For each token: gate → (suspect → mlm → (ambiguous → llm)).
      4. Drain events; build ``PageCorrections``; return.
    """

    nakdan_gate: ICascadeStage
    mlm_scorer: ICascadeStage
    llm_reviewer: ICascadeStage
    feedback: FeedbackReadPort
    listeners: Sequence[EventListener] = field(default_factory=tuple)

    # ---- entry point ------------------------------------------------------

    def run_page(
        self,
        tokens: Sequence[str],
        sentences: Sequence[SentenceContext],
        *,
        page_index: int,
        sha: str,
        mode: CascadeMode,
    ) -> PageCorrections:
        """Run the cascade across a page's tokens.

        TODO AC-F48-S01/AC-01 (T-05): construct ``CorrectionCascade``
            aggregate; ``lock_mode(mode)``; configure llm cap from policy.
        TODO BT-211 (T-05): consult ``feedback.user_rejections(sha)``
            to override matching tokens to ``keep_original``.
        TODO AC-F48-S01/AC-01 (T-05): walk tokens; record each verdict
            via ``aggregate.record_decision`` (which enforces INV-CCS-001
            via ``TokenInTokenOutPolicy``).
        TODO AC-F48-S03/AC-02 (T-05): when mode == "no_llm" or
            ``aggregate.llm_cap_reached()``, skip stage 3 — ambiguous
            verdict short-circuits to ``keep_original``.
        TODO AC-F48-S06/AC-01..04 (T-05): when mode == "no_mlm", skip
            stage 2; suspect tokens go to deprecated
            ``_KNOWN_OCR_FIXES`` lookup (T-07).
        TODO AC-F48-S04/AC-01 (T-05): drain events; publish snapshots
            to every listener; return ``PageCorrections``.
        """
        raise NotImplementedError(
            "AC-F48-S01/AC-01 / AC-F48-S03/AC-02 / AC-F48-S06/AC-01 — "
            "TDD T-05 fills"
        )

    # ---- listener fan-out (T-05) ------------------------------------------

    def _publish(
        self,
        applied: Iterable[CorrectionApplied],
        rejected: Iterable[CorrectionRejected],
        mode_events: Iterable[CascadeModeDegraded],
        cap_events: Iterable[LLMCallCapReached],
    ) -> None:
        """Fan out drained events to every registered listener.

        TODO T-05: for each event, call the matching listener method on
            every listener; swallow listener exceptions (audit-resilient
            per ADR-033) but record via ``CorrectionRejected`` log line.
        """
        raise NotImplementedError("AC-F48-S01/AC-01 — TDD T-05 fills")


__all__ = [
    "EventListener",
    "PageCorrections",
    "CorrectionCascadeService",
]
