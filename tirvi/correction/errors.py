"""Typed domain errors for the F48 correction cascade.

Spec: F48 DE-05 / DE-04 / DE-06 / DE-08.

Errors are raised by policies / aggregates / log writers; never by ports.
TDD fills the bodies that raise them.
"""

from __future__ import annotations


class CascadeError(Exception):
    """Base error for any F48 cascade fault."""


class CascadeInvariantViolation(CascadeError):
    """INV-CCS-001 / INV-CCS-002 / INV-CCS-003 violation.

    Hard error — should never escape ``CorrectionCascadeService``;
    caught and logged via ``CorrectionRejected`` event when possible.
    """


class CascadeConfigInvalid(CascadeError):
    """INV-CCS-005 / general config validation (BT-219, T-07).

    Raised when:
      - mode is locked twice with different names (INV-CCS-005).
      - threshold tuple invalid (low >= high).
      - confusion_pairs.yaml missing or malformed (NT-01 — T-08).
    """


class ConfusionTableMissing(CascadeConfigInvalid):
    """``confusion_pairs.yaml`` is missing on cascade init (NT-01)."""


class LLMParseFailure(CascadeError):
    """LLM response did not parse to ``{verdict, chosen, reason}`` (NT-02)."""


class LLMWordListViolation(CascadeError):
    """INV-CCS-002 — LLM chose a word outside candidates / word-list (NT-03)."""


class AuditGapWriteFailure(CascadeError):
    """Disk-full / IO error writing ``corrections.json`` (FT-324, T-06).

    Pipeline does NOT abort on this error; the cascade catches and routes
    to ``audit_gaps.json``.
    """


__all__ = [
    "CascadeError",
    "CascadeInvariantViolation",
    "CascadeConfigInvalid",
    "ConfusionTableMissing",
    "LLMParseFailure",
    "LLMWordListViolation",
    "AuditGapWriteFailure",
]
