"""F15 DE-05 — URL / embedded-acronym skip filter."""

from __future__ import annotations

import re

_LOWER_HOSTLIKE = re.compile(r"^[a-z]+\.[a-z]")


def should_skip(token: str) -> bool:
    """True if ``token`` should bypass acronym lookup (URL-like)."""
    if "://" in token:
        return True
    if token.startswith("www."):
        return True
    if _LOWER_HOSTLIKE.match(token):
        return True
    return False
