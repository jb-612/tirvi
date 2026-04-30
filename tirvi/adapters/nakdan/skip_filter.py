"""F19 T-04 — Token-skip filter for the diacritization stage.

Spec: N02/F19 DE-04. AC: US-01/AC-01. FT-anchors: FT-149.

Tokens skipped here keep their original surface form and emit confidence
``None`` (per biz S01 — never ``0.0``). Saves model invocation cost on
material the seq2seq head cannot diacritize anyway (English, digits,
punctuation only).
"""

from __future__ import annotations

import re

_HEBREW_RE = re.compile(r"[֐-׿]")
_NON_WORD_ONLY_RE = re.compile(r"^[\d\s\W]+$")
_SKIP_POS = frozenset({"NUM", "PUNCT"})


def should_skip_diacritization(
    text: str,
    lang_hint: str | None = None,
    pos: str | None = None,
) -> bool:
    """Return True when the token should bypass the Nakdan inference call."""
    if lang_hint == "en":
        return True
    if pos in _SKIP_POS:
        return True
    if not _HEBREW_RE.search(text):
        return True
    return bool(_NON_WORD_ONLY_RE.match(text))
