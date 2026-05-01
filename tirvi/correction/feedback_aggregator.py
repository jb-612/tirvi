"""FeedbackAggregator — threshold-gated rule promotion suggestions (DE-08).

Spec: F48 DE-08. AC: F48-S05/AC-01..AC-04.
T-08.

Reads ``drafts/feedback.db`` (sqlite — schema-compat extension of F47's
``BO46 FeedbackEntry``: adds ``system_chose``, ``expected``,
``persona_role``, ``sentence_context_hash``).

Aggregator logic:
  - Group rows by ``(ocr_word, expected)``.
  - **Per-sha cap = 1** (anti-spam, INV-CCS-006, BT-220).
  - Emit ``RuleSuggestion`` only when ``distinct_shas >= 3``.
  - Output to ``drafts/rule_suggestions.json``; engineer-gated, never
    auto-applies.

Strict scaffold rule: NO BUSINESS LOGIC.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .domain.events import RulePromoted
from .domain.policies import PerShaContributionCapPolicy
from .ports import FeedbackReadPort

DEFAULT_DISTINCT_SHA_THRESHOLD: int = 3


@dataclass(frozen=True)
class RuleSuggestion:
    """One row in ``drafts/rule_suggestions.json`` (BO56).

    AC: F48-S05/AC-03, F48-S05/AC-04.
    """

    ocr_word: str
    expected: str
    support_count: int          # = distinct_shas (after per-sha cap)
    distinct_shas: int
    sample_sentence_hashes: tuple[str, ...] = ()


@dataclass
class FeedbackAggregator:
    """CLI entry point for the rule-promotion aggregator (DE-08)."""

    feedback: FeedbackReadPort
    output_path: Path
    cap_policy: PerShaContributionCapPolicy = field(
        default_factory=PerShaContributionCapPolicy
    )
    distinct_sha_threshold: int = DEFAULT_DISTINCT_SHA_THRESHOLD

    def run(self) -> tuple[RuleSuggestion, ...]:
        """Aggregate feedback rows; write suggestions; return them.

        TODO AC-F48-S05/AC-01 (T-08): scan all known shas via
            ``feedback.user_rejections(sha)`` for each sha.
        TODO AC-F48-S05/AC-02 (T-08): group by ``(ocr_word, expected)``.
        TODO INV-CCS-006 / BT-220 (T-08): apply
            ``self.cap_policy.cap_per_sha`` so each sha contributes ≤ 1.
        TODO AC-F48-S05/AC-03 (T-08): emit ``RuleSuggestion`` for each
            group with ``distinct_shas >= self.distinct_sha_threshold``.
        TODO AC-F48-S05/AC-04 (T-08): write to ``self.output_path``
            atomically; return the suggestions tuple.
        """
        raise NotImplementedError(
            "AC-F48-S05/AC-01..AC-04 / FT-325 / INV-CCS-006 — TDD T-08 fills"
        )

    def _emit_rule_promoted(self, sugg: RuleSuggestion) -> RulePromoted:
        """Build a ``RulePromoted`` domain event from a suggestion.

        TODO T-08: stamp ``occurred_at`` from injected clock; return
        ``RulePromoted`` for the in-process listener bus.
        """
        raise NotImplementedError("AC-F48-S05/AC-03 — TDD T-08 fills")


__all__ = [
    "FeedbackAggregator",
    "RuleSuggestion",
    "DEFAULT_DISTINCT_SHA_THRESHOLD",
]
