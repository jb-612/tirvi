"""Strip OCR-induced artefacts that confuse Nakdan or Phonikud.

Tesseract picks up:
  - Gender-inclusive slashes:  ``לנבחן/ת`` — Nakdan splits into two
    entries, second is just ``ת`` which Phonikud reads as the letter
    name "Tav". Drop the ``/<suffix>`` and read just the masculine.
  - ASCII double-apostrophe wrapping a word:  ``(''סגורות'').`` —
    Nakdan reads the trailing ``''`` as gershayim (״, acronym marker)
    and appends ``ָא`` to the diacritization. Strip wrapping
    quotes/parentheses so the bare word reaches Nakdan.
"""

from __future__ import annotations

import re

# Specific gender-marker suffixes after a slash. We don't accept "any 1-3
# Hebrew letters" because "או" (or) is a word — see ``ו/או`` (and/or).
_SLASH_SUFFIX_PAT = re.compile(r"/(?:ת|ות|ית|ים|ין|ה)\b")

# Wrapping characters that confuse Nakdan when adjacent to a word.
# Each char in this set is stripped from the start and end of every token.
_WRAP_CHARS = "(){}[]''\"\"“”‘’״׳"


def strip_slash_suffix(word: str) -> str:
    """Remove gender-inclusive ``/<suffix>`` at end of word.

    'לנבחן/ת'  → 'לנבחן'
    'סטודנט/ית' → 'סטודנט'
    'ו/או' → 'ו/או'  (suffix > 3 letters, untouched)
    """
    return _SLASH_SUFFIX_PAT.sub("", word)


def strip_wrap_chars(word: str) -> str:
    """Remove wrapping quote/paren chars but preserve trailing punctuation.

    Strips:        ``(''סגורות'').`` → ``סגורות.``
    Doesn't touch: ``לפניך``         → ``לפניך``
    """
    # Identify final sentence punctuation to re-attach
    trailing = ""
    while word and word[-1] in ".,!?:;":
        trailing = word[-1] + trailing
        word = word[:-1]
    # Strip wrap chars from both ends
    while word and word[0] in _WRAP_CHARS:
        word = word[1:]
    while word and word[-1] in _WRAP_CHARS:
        word = word[:-1]
    return word + trailing


def clean_ocr_artifacts(words: list[str]) -> list[str]:
    """Apply all OCR-artefact strippers to each word."""
    return [strip_wrap_chars(strip_slash_suffix(w)) for w in words]
