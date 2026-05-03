"""F52 DE-02 — Hebrew block-classifier cue lexicon.

Curated cue constants factored out of classifier.py so maintainers can
extend the lexicon without touching classifier control flow.

Spec: N02/F52 DE-02. AC: F52-S01/AC-02, F52-S02/AC-01.
"""

import re

# Prefixes that identify instruction blocks (must come first in leading words).
INSTRUCTION_PREFIXES: tuple[str, ...] = ("הוראות", "קרא בעיון", "שים לב")

# Prefixes that identify datum / supporting-data blocks.
DATUM_PREFIXES: tuple[str, ...] = ("נתונים",)

# Pattern matching a single Hebrew letter-choice prefix (א./ב./ג./ד.).
LETTER_CHOICE_RE = re.compile(r"^[א-ד]\.$")
