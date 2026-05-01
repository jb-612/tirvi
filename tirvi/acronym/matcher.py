"""F15 — whole-token matcher with sentence-final punctuation strip-reattach.

Spec: N02/F15 DE-03.
"""

from __future__ import annotations

from tirvi.acronym.value_objects import AcronymEntry, Lexicon

_TRAILING_PUNCT = ".,?:!׃"  # ASCII final punctuation + Hebrew sof-pasuq


def _split_trailing(token: str) -> tuple[str, str]:
    end = len(token)
    while end > 0 and token[end - 1] in _TRAILING_PUNCT:
        end -= 1
    return token[:end], token[end:]


def match_token(token: str, lexicon: Lexicon) -> tuple[AcronymEntry, str] | None:
    """Look up ``token`` in ``lexicon`` after stripping trailing punctuation.

    Returns ``(entry, trailing)`` on hit; ``None`` on miss. Geresh ``׳`` and
    gershayim ``״`` belong to the form and are never stripped.
    """
    bare, trailing = _split_trailing(token)
    entry = lexicon._index.get(bare)
    if entry is None:
        return None
    return entry, trailing
