"""F18 — disambiguation errors."""

from tirvi.errors import AdapterError


class DisambiguationError(AdapterError):
    """Raised when no candidate sense passes the margin threshold.

    Spec: N02/F18 DE-03.
    """
