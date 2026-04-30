"""F18 — disambiguation errors."""

from tirvi.errors import AdapterError


class DisambiguationError(AdapterError):
    """Raised when no candidate sense passes the margin threshold.

    Spec: N02/F18 DE-03.
    """


class MorphKeyOutOfScope(AdapterError):
    """Raised when a morph_features dict contains a key outside the POC
    whitelist (gender / number / person / tense / def / case).

    Spec: N02/F18 DE-02.
    """
