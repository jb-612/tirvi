"""F15 DE-06 — unknown-acronym candidate detection (spell-out fallback)."""

from __future__ import annotations

import re

_UPPER_LATIN = re.compile(r"^[A-Z]{2,6}$")


def is_acronym_candidate(token: str) -> bool:
    """True if token looks like an acronym (Hebrew or 2-6 upper Latin)."""
    if "׳" in token or "״" in token:
        return True
    return bool(_UPPER_LATIN.match(token))
