"""Kamatz katan post-Nakdan normalization.

Phonikud reads kamatz (ָ) as /a/, but in classic kamatz-katan positions
the correct phoneme is /o/. Workaround: replace kamatz with cholam (וֹ)
in known kamatz-katan words BEFORE sending to G2P.

Reference: Even-Shoshan / Hebrew Academy phonology table.
Coverage is intentionally narrow — false positives are worse than misses.
"""
from __future__ import annotations
import re

# Known kamatz-katan stems and their correctly-vocalized replacements.
# Each maps a Nakdan-output form (or a regex) to the cholam-bearing form.
_KAMATZ_KATAN_FIXES: list[tuple[str, str]] = [
    # כָּל-family (every, in every, to every, from every, all of)
    ("כָּל",   "כֹּל"),
    ("כָל",    "כֹל"),
    # Compounds with prefixes (the kamatz on כל stays kamatz-katan)
    ("בְּכָל",  "בְּכֹל"),
    ("בְכָל",   "בְכֹל"),
    ("לְכָל",   "לְכֹל"),
    ("מִכָּל",  "מִכֹּל"),
    ("שֶׁכָּל", "שֶׁכֹּל"),
    ("וְכָל",   "וְכֹל"),
    ("וכל",    "וכֹּל"),
    # Other common kamatz-katan words
    ("חָכְמָה",  "חוֹכְמָה"),
    ("צָהֳרַיִם", "צוֹהֳרַיִם"),
    ("אָזְנַיִם", "אוֹזְנַיִם"),
    ("עָנְיָן",   "עוֹנְיָן"),
    ("רָגְזָה",   "רוֹגְזָה"),
]


import re as _re


def fix_kamatz_katan(diacritized_text: str) -> str:
    """Replace kamatz with cholam in known kamatz-katan words.

    Word-boundary aware so substrings inside larger words are NOT replaced:
    e.g. ``כָּל`` won't match inside ``כַּלְכָּלָה`` (kalkala).
    """
    result = diacritized_text
    for wrong, right in _KAMATZ_KATAN_FIXES:
        # (?<![א-ת]) and (?![א-ת]) — Hebrew letter must not flank the match
        pattern = r"(?<![א-ת])" + _re.escape(wrong) + r"(?![א-ת])"
        result = _re.sub(pattern, right, result)
    return result


def _fix_kamatz_katan_OLD(diacritized_text: str) -> str:
    """Kept for compatibility — used by legacy callers (none currently)."""
    result = diacritized_text
    for wrong, right in _KAMATZ_KATAN_FIXES:
        result = result.replace(wrong, right)
    return result
