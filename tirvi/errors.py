"""Domain errors for adapter-port contract violations (F03 L3)."""


class AdapterError(Exception):
    """Base class for every adapter-related domain error."""


class SchemaContractError(AdapterError):
    """Raised by ``assert_adapter_contract`` when an adapter returns the wrong shape.

    Invariant: BT-009 — adapter must return its result type, not raw ``bytes``.
    Spec: F03 DE-05.
    """


class WordTimingFallbackError(AdapterError):
    """Raised when the WordTimingProvider exhausts both adapters.

    Invariant: BT-012 — forced-alignment is the last resort; if it also fails,
    the error surface is typed (not a silent fallthrough).
    Spec: F03 DE-03, ADR-015.
    """


class MarkCountMismatchError(AdapterError):
    """Raised when ``len(marks) != len(transcript_tokens)`` AND truncation was
    NOT signalled by the TTS adapter (genuine adapter bug, not graceful path).

    Spec: F30 DE-05 (post-review C2). When truncation IS signalled, F30 aligns
    by ``min(marks, tokens)`` and emits a warning instead.
    """
