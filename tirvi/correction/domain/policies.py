"""Domain policies — invariants for the F48 correction cascade.

Spec: F48 DE-05 / DE-04.

Each policy is a named class with a single ``check(...)`` method whose
body is ``raise NotImplementedError`` until TDD fills it. Policies own
the WHAT — the HOW lives in the aggregate / service.

Invariant catalogue (from ``traceability.yaml`` `bounded_contexts`):
  INV-CCS-001 (DE-05): token-in / token-out — never split or merge tokens.
  INV-CCS-002 (DE-04): chosen ∈ candidates ∧ chosen ∈ NakdanWordList.
  INV-CCS-003 (DE-06): every corrected token has a CorrectionLogEntry.
  INV-CCS-004 (DE-04): outbound DNS resolves only to 127.0.0.1 / ::1.
  INV-CCS-005 (DE-07): mode is fixed per-page once selected.
  INV-CCS-006 (DE-08): per-sha contribution to support_count is capped at 1.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..ports import NakdanWordListPort
from ..value_objects import CorrectionVerdict


@dataclass(frozen=True)
class TokenInTokenOutPolicy:
    """INV-CCS-001 — corrected token must be exactly one whitespace-free
    Hebrew token; no splits, no merges.

    AC: F48-S01/AC-01 (cascade output shape — DEP-052/053).
    """

    def check(self, original: str, verdict: CorrectionVerdict) -> None:
        # TODO INV-CCS-001 (T-05): assert verdict.corrected_or_none is None
        #   OR contains no whitespace AND yields exactly 1 token under split().
        # On violation raise CascadeInvariantViolation with original + verdict.
        raise NotImplementedError("AC-F48-S01/AC-01 / INV-CCS-001 — TDD T-05 fills")


@dataclass(frozen=True)
class AntiHallucinationPolicy:
    """INV-CCS-002 — LLM reviewer chose word must be in candidates AND in
    NakdanWordList.

    AC: F48-S03/AC-03. NT-03 / NT-05 cover the negative paths.

    Wired with a ``NakdanWordListPort`` so the same word-list source feeds
    NakdanGate AND the anti-hallucination check (no parallel truth).
    """

    word_list: NakdanWordListPort

    def check(
        self, chosen: str, candidates: tuple[str, ...]
    ) -> None:
        # TODO INV-CCS-002 (T-04b): reject if chosen not in candidates.
        # TODO INV-CCS-002 (T-04b): reject if not self.word_list.is_known_word(chosen).
        # On violation: raise LLMWordListViolation (errors.py).
        raise NotImplementedError("AC-F48-S03/AC-03 / INV-CCS-002 — TDD T-04b fills")


@dataclass(frozen=True)
class PerPageLLMCapPolicy:
    """BT-F-05 — per-page LLM-call cap (default 10).

    Once cap reached, subsequent suspect tokens short-circuit to
    ``keep_original`` and the cascade emits ``LLMCallCapReached``.

    AC: F48-S03/AC-02.
    """

    cap: int = 10

    def can_call(self, calls_made: int) -> bool:
        # TODO BT-F-05 (T-04a): return calls_made < self.cap.
        raise NotImplementedError("AC-F48-S03/AC-02 / BT-F-05 — TDD T-04a fills")


@dataclass(frozen=True)
class PerShaContributionCapPolicy:
    """INV-CCS-006 — per-sha contribution to support_count is capped at 1.

    Anti-spam: the same draft cannot inflate the rule-promotion threshold.

    AC: F48-S05/AC-04. BT-220 covers.
    """

    def cap_per_sha(self, raw_counts_per_sha: dict[str, int]) -> int:
        # TODO INV-CCS-006 (T-08): support_count = number of shas with
        # >= 1 contribution (i.e., len({sha for sha, n in raw if n >= 1})).
        raise NotImplementedError("AC-F48-S05/AC-04 / INV-CCS-006 — TDD T-08 fills")


@dataclass(frozen=True)
class PerPageModeFixedPolicy:
    """INV-CCS-005 — mode is fixed per-page once selected; no mid-page flip.

    AC: F48-S06/AC-01..AC-04. BT-213 covers.
    """

    def lock(self, current_mode_name: str | None, proposed_mode_name: str) -> str:
        # TODO INV-CCS-005 (T-07): if current is None, accept; otherwise
        # raise CascadeConfigInvalid("mid-page mode flip rejected").
        raise NotImplementedError("AC-F48-S06/AC-01 / INV-CCS-005 — TDD T-07 fills")


__all__ = [
    "TokenInTokenOutPolicy",
    "AntiHallucinationPolicy",
    "PerPageLLMCapPolicy",
    "PerShaContributionCapPolicy",
    "PerPageModeFixedPolicy",
]
