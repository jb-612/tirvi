"""Port Protocols for the F48 correction cascade.

Spec: F48 DE-01.
ADR-029: no vendor SDK types in port signatures.
ADR-013: every port is ``@runtime_checkable``; consumed via duck-typed
DI in ``CorrectionCascadeService``.

Each method body is intentionally a Protocol ellipsis — concrete classes
implementing these ports raise ``NotImplementedError`` until TDD fills
the bodies.
"""

from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from .value_objects import CorrectionVerdict, SentenceContext, UserRejection


@runtime_checkable
class ICascadeStage(Protocol):
    """Single-method cascade stage port (DE-01).

    Implemented by NakdanGate, DictaBertMLMScorer, OllamaLLMReviewer.

    AC: F48-S01/AC-01, F48-S02/AC-02, F48-S03/AC-01.
    """

    def evaluate(
        self, token: str, context: SentenceContext
    ) -> CorrectionVerdict:  # pragma: no cover — Protocol
        ...


@runtime_checkable
class NakdanWordListPort(Protocol):
    """Port for the Nakdan word-list lookup (CO13).

    Used by NakdanGate (DE-02) and as the anti-hallucination check inside
    OllamaLLMReviewer (DE-04, INV-CCS-002).

    AC: F48-S01/AC-01.
    """

    def is_known_word(self, token: str) -> bool:  # pragma: no cover — Protocol
        ...


@runtime_checkable
class LLMClientPort(Protocol):
    """Port for the local Ollama LLM HTTP client (DE-04).

    The single vendor-boundary seam — concrete adapter in
    ``tirvi/correction/adapters/ollama.py`` is the only file allowed
    to import ``httpx`` / ``requests`` (ADR-029).

    AC: F48-S03/AC-02.
    """

    def generate(
        self,
        prompt: str,
        model_id: str,
        temperature: float,
        seed: int,
    ) -> str:  # pragma: no cover — Protocol
        ...


@runtime_checkable
class FeedbackReadPort(Protocol):
    """Port for reading user-rejection feedback (DE-08).

    The cascade reads at init to revert previously-rejected corrections
    (BT-211). Aggregator (DE-08) reads to compute rule promotion.

    AC: F48-S05/AC-01.
    """

    def user_rejections(
        self, draft_sha: str
    ) -> Iterable[UserRejection]:  # pragma: no cover — Protocol
        ...


__all__ = [
    "ICascadeStage",
    "NakdanWordListPort",
    "LLMClientPort",
    "FeedbackReadPort",
]
