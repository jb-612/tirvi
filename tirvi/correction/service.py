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
        *,
        sentences: Sequence[SentenceContext] | None = None,
        page_index: int = 0,
        sha: str = "",
        mode: CascadeMode,
    ) -> PageCorrections:
        agg = CorrectionCascade(page_index=page_index, sha=sha)
        agg.lock_mode(mode)
        rejections = self._load_rejections(sha)
        corrected: list[str] = []
        for i, token in enumerate(tokens):
            ctx = self._ctx(sentences, i, page_index)
            if self._is_rejected(token, rejections):
                verdict = self._user_rejection_verdict(token)
            else:
                verdict = self._dispatch(token, ctx, mode)
            agg.record_decision(verdict)
            corrected.append(verdict.corrected_or_none or token)
        applied, rejected, mode_events, cap_events = agg.drain_events()
        self._publish(applied, rejected, mode_events, cap_events)
        return PageCorrections(
            page_index=page_index, sha=sha,
            original_tokens=tuple(tokens),
            corrected_tokens=tuple(corrected),
            stage_decisions=agg.stage_decisions,
            mode=mode,
            applied=applied, rejected=rejected,
            mode_events=mode_events, cap_events=cap_events,
        )

    def _dispatch(self, token: str, ctx: SentenceContext, mode: CascadeMode) -> CorrectionVerdict:
        if mode.name == "bypass":
            return self._passthrough(token)
        gate_v = self.nakdan_gate.evaluate(token, ctx)
        if gate_v.verdict != "suspect":
            return gate_v
        return self._after_gate(token, ctx, mode)

    def _after_gate(self, token: str, ctx: SentenceContext, mode: CascadeMode) -> CorrectionVerdict:
        if mode.name == "no_mlm":
            return self._passthrough(token)
        mlm_v = self.mlm_scorer.evaluate(token, ctx)
        if mlm_v.verdict == "auto_apply":
            return mlm_v
        return self._llm_or_skip(token, ctx, mode)

    def _llm_or_skip(self, token: str, ctx: SentenceContext, mode: CascadeMode) -> CorrectionVerdict:
        if mode.name == "no_llm":
            return self._passthrough(token)
        return self.llm_reviewer.evaluate(token, ctx)

    def _load_rejections(self, sha: str) -> set[str]:
        if not sha:
            return set()
        return {r.ocr_word for r in self.feedback.user_rejections(sha)}

    def _is_rejected(self, token: str, rejections: set[str]) -> bool:
        return token in rejections

    def _user_rejection_verdict(self, token: str) -> CorrectionVerdict:
        return CorrectionVerdict(
            stage="nakdan_gate", verdict="keep_original",
            original=token, reason="user_override",
        )

    def _passthrough(self, token: str) -> CorrectionVerdict:
        return CorrectionVerdict(stage="nakdan_gate", verdict="pass", original=token)

    def _ctx(self, sentences: Sequence[SentenceContext] | None, i: int, page_index: int) -> SentenceContext:
        if sentences and i < len(sentences):
            return sentences[i]
        return SentenceContext(sentence_text="", sentence_hash="", page_index=page_index, token_index=i)

    # ---- listener fan-out (T-05) ------------------------------------------

    def _publish(
        self,
        applied: Iterable[CorrectionApplied],
        rejected: Iterable[CorrectionRejected],
        mode_events: Iterable[CascadeModeDegraded],
        cap_events: Iterable[LLMCallCapReached],
    ) -> None:
        for e in applied:
            for listener in self.listeners:
                self._safe_call(listener.on_correction_applied, e)
        for e in rejected:
            for listener in self.listeners:
                self._safe_call(listener.on_correction_rejected, e)
        for e in mode_events:
            for listener in self.listeners:
                self._safe_call(listener.on_cascade_mode_degraded, e)
        for e in cap_events:
            for listener in self.listeners:
                self._safe_call(listener.on_llm_call_cap_reached, e)

    def _safe_call(self, fn, event) -> None:  # type: ignore[override]
        try:
            fn(event)
        except Exception:
            pass


__all__ = [
    "EventListener",
    "PageCorrections",
    "CorrectionCascadeService",
]
