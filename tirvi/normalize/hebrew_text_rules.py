"""Hebrew-specific text normalization rules for exam PDFs.

Rules applied before diacritization so Nakdan gets clean input:

  expand_gender_slash   — לנבחן/ת → לנבחן, נבחנת
  expand_geresh_ordinal — א׳ → אלף ,  ב׳ → בית
"""

from __future__ import annotations

import re

# -----------------------------------------------------------------------
# Geresh ordinal expansion
# -----------------------------------------------------------------------

GERESH = "׳"  # ׳  Hebrew punctuation geresh (not U+0027 apostrophe)

_LETTER_NAMES: dict[str, str] = {
    "א": "אלף",  "ב": "בית",  "ג": "גימל", "ד": "דלת",  "ה": "הא",
    "ו": "וו",   "ז": "זין",  "ח": "חית",  "ט": "טית",  "י": "יוד",
    "כ": "כף",   "ך": "כף",   "ל": "למד",  "מ": "מם",   "ם": "מם",
    "נ": "נון",  "ן": "נון",  "ס": "סמך",  "ע": "עין",  "פ": "פא",
    "ף": "פא",   "צ": "צדי",  "ץ": "צדי",  "ק": "קוף",  "ר": "ריש",
    "ש": "שין",  "ת": "תא",
}

_GERESH_PAT = re.compile(r"([א-ת])" + GERESH)


def expand_geresh_ordinal(text: str) -> str:
    """Replace letter+geresh with the Hebrew letter name.

    'חלק א׳' → 'חלק אלף'
    """
    return _GERESH_PAT.sub(lambda m: _LETTER_NAMES.get(m.group(1), m.group(1)), text)


# -----------------------------------------------------------------------
# Gender-inclusive slash expansion
# -----------------------------------------------------------------------

# Final-form → regular-form conversions needed when building feminine stem
_SOFIT_TO_REGULAR: dict[str, str] = {
    "ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ",
}

# Single-char Hebrew word-prefix letters
_PREFIXES = frozenset("בוכלמשה")

_SLASH_PAT = re.compile(r"([א-ת]+)/([א-ת]+)")


def expand_gender_slash(text: str) -> str:
    """Expand gender-inclusive slash notation.

    'לנבחן/ת'    → 'לנבחן, נבחנת'
    'סטודנט/ית'  → 'סטודנט, סטודנטית'
    """
    def _replace(m: re.Match) -> str:
        masculine = m.group(1)
        suffix = m.group(2)
        # Determine stem: strip single-char prefix so ל+stem → stem+suffix
        if len(masculine) > 2 and masculine[0] in _PREFIXES:
            stem = masculine[1:]
        else:
            stem = masculine
        # Convert final-form last letter to regular form before appending suffix
        if stem and stem[-1] in _SOFIT_TO_REGULAR:
            stem = stem[:-1] + _SOFIT_TO_REGULAR[stem[-1]]
        feminine = stem + suffix
        return f"{masculine}, {feminine}"

    return _SLASH_PAT.sub(_replace, text)


# -----------------------------------------------------------------------
# Combined entry point
# -----------------------------------------------------------------------

def apply_hebrew_text_rules(text: str) -> str:
    """Apply all Hebrew text normalisation rules in the correct order."""
    text = expand_geresh_ordinal(text)
    text = expand_gender_slash(text)
    return text
