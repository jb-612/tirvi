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


def fix_kamatz_katan(diacritized_text: str) -> str:
    """Replace kamatz with cholam in known kamatz-katan words."""
    result = diacritized_text
    for wrong, right in _KAMATZ_KATAN_FIXES:
        result = result.replace(wrong, right)
    return result
