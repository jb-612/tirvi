"""Value objects for the F48 correction cascade.

Spec: F48 DE-01. ADR-029 (no vendor types in domain).

Frozen dataclasses + Literal enums; no business logic — value-object
construction may only validate truthy / structural shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Verdict enum (Literal — biz BO52 StageDecision.verdict surface)
# ---------------------------------------------------------------------------

CorrectionVerdictName = Literal[
    "pass",              # NakdanGate happy path — token is a known Hebrew word
    "suspect",           # NakdanGate forwards to MLM
    "keep_original",     # MLM/LLM decides not to change
    "ambiguous",         # MLM cannot decide (delta in [low, high))
    "auto_apply",        # MLM auto-applies (delta >= high + margin satisfied)
    "apply",             # LLM reviewer accepts a candidate
    "skip_empty",        # NakdanGate skip — empty token after normalize (NT-04)
    "skip_short",        # NakdanGate skip — len < 2 (BT-F-03)
    "skip_non_hebrew",   # NakdanGate skip — digit / Latin token
]


# ---------------------------------------------------------------------------
# Cascade mode (DE-07)
# ---------------------------------------------------------------------------

CascadeModeName = Literal[
    "full",              # NakdanGate + MLM + LLM all healthy
    "no_llm",            # Ollama unreachable; stricter MLM threshold (FT-326)
    "no_mlm",            # DictaBERT failed to load; deprecated _KNOWN_OCR_FIXES (FT-327)
    "emergency_fixes",   # NakdanGate also unloaded; only deprecated table
    "bypass",            # all stages failed; identity passthrough
]


@dataclass(frozen=True)
class CascadeMode:
    """Per-page cascade mode (DE-07).

    Invariants (TDD fills):
      - INV-CCS-005: mode is fixed per-page once selected; no mid-page flip.
    """

    name: CascadeModeName
    reason: str | None = None  # human-readable reason for non-"full" modes


# ---------------------------------------------------------------------------
# Sentence context (input to ICascadeStage.evaluate)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SentenceContext:
    """Context passed to every cascade stage.

    Carries the sentence the suspect token sits in, plus a stable hash
    used as part of the MLM and LLM cache keys (DE-03 / DE-04 / ADR-034).
    """

    sentence_text: str
    sentence_hash: str
    page_index: int = 0
    token_index: int = 0


# ---------------------------------------------------------------------------
# CorrectionVerdict (BO52 surface — single port return type)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CorrectionVerdict:
    """Result of a single cascade stage's evaluation of a token.

    Spec: F48 DE-01.
    AC: F48-S01/AC-01, F48-S02/AC-02, F48-S03/AC-01, F48-S04/AC-01.
    BO: BO52 StageDecision (the auditable shape).

    Invariants (TDD fills):
      - INV-CCS-001 (DE-05): token-in / token-out — corrected_or_none
        must encode exactly ONE token (no whitespace splits, no merges).
      - INV-CCS-002 (DE-04): if stage="llm_reviewer" and verdict="apply",
        then ``corrected_or_none in candidates`` and the chosen word is
        a known Hebrew word.
    """

    stage: Literal["nakdan_gate", "mlm_scorer", "llm_reviewer", "deprecated_table"]
    verdict: CorrectionVerdictName
    original: str
    corrected_or_none: str | None = None
    score: float | None = None
    candidates: tuple[str, ...] = ()
    mode: CascadeMode | None = None
    cache_hit: bool = False
    reason: str | None = None
    model_versions: dict[str, str] = field(default_factory=dict)
    prompt_template_version: str | None = None


# ---------------------------------------------------------------------------
# Feedback inputs (DE-08)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class UserRejection:
    """A teacher-QA "no" vote on a previous correction (BT-211).

    Read by the cascade at init via FeedbackReadPort; matching tokens
    are forced to verdict="keep_original".
    """

    ocr_word: str
    system_chose: str
    expected: str | None
    persona_role: str
    sentence_context_hash: str
    draft_sha: str


__all__ = [
    "CorrectionVerdict",
    "CorrectionVerdictName",
    "SentenceContext",
    "CascadeMode",
    "CascadeModeName",
    "UserRejection",
]
