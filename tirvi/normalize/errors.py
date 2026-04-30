"""F14 — normalization errors."""

from tirvi.errors import AdapterError


class NormalizationError(AdapterError):
    """Raised when normalization cannot produce a clean span map.

    Spec: N02/F14 DE-05.
    """
