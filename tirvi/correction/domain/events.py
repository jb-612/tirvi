"""Domain events emitted by the F48 correction cascade.

Spec: F48 DE-05.
BO refs: BO57 CorrectionApplied, BO58 CorrectionRejected,
         BO59 CascadeModeDegraded.

In-process pub-sub only — no infrastructure (ADR-033). Listeners are
registered through ``CorrectionCascadeService`` constructor; no broker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..value_objects import CascadeMode


@dataclass(frozen=True)
class CorrectionApplied:
    """A correction was applied to a token (BO57).

    AC: F48-S02/AC-03, F48-S03/AC-01.
    Emitted by: CorrectionCascadeService when verdict in
    {auto_apply, apply}.
    """

    page_index: int
    original: str
    corrected: str
    chosen_by_stage: str          # "mlm_scorer" | "llm_reviewer"
    score: float | None
    sentence_hash: str
    occurred_at: datetime


@dataclass(frozen=True)
class CorrectionRejected:
    """A candidate correction was rejected (BO58).

    AC: F48-S03/AC-03, F48-S04/AC-02.
    Emitted on:
      - LLM anti-hallucination guard fired (chosen ∉ candidates / NakdanWordList)
      - LLM parse failure (NT-02 / NT-03)
      - User-rejection override at init (BT-211)
    """

    page_index: int
    original: str
    proposed: str | None
    rejected_by: str              # "anti_hallucination" | "parse_failure" | "user_override"
    sentence_hash: str
    reason: str
    occurred_at: datetime


@dataclass(frozen=True)
class CascadeModeDegraded:
    """Cascade is running in a non-"full" mode for this page (BO59).

    AC: F48-S06/AC-01..AC-04.
    Emitted by: HealthProbe at init or by CorrectionCascadeService
    when a stage fails open. Consumed by F50 inspector banner.
    """

    page_index: int
    mode: CascadeMode
    occurred_at: datetime
    healthcheck_summary: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class LLMCallCapReached:
    """The per-page LLM-call cap was reached (BT-F-05).

    AC: F48-S03/AC-02 (cap pathway).
    Emitted by: OllamaLLMReviewer / LLMClientPort adapter when call count
    on the current page reaches the configured cap (default 10). Subsequent
    suspect tokens short-circuit to verdict="keep_original".
    """

    page_index: int
    calls_made: int
    cap: int
    occurred_at: datetime


@dataclass(frozen=True)
class RulePromoted:
    """A confusion-pair correction was *suggested* for promotion (BO56 surface).

    AC: F48-S05/AC-03.
    Emitted by: FeedbackAggregator (DE-08) — never auto-applied;
    engineer reviews `drafts/rule_suggestions.json`.

    Per-sha cap = 1 (anti-spam, INV-CCS-006).
    """

    ocr_word: str
    expected: str
    support_count: int
    distinct_shas: int
    occurred_at: datetime


__all__ = [
    "CorrectionApplied",
    "CorrectionRejected",
    "CascadeModeDegraded",
    "LLMCallCapReached",
    "RulePromoted",
]
