"""Function-word lemma lexicon — small curated set used by ADR-039.

When DictaBERT-Morph tags a token as ADP or SCONJ, the inference
layer prefers Dicta candidates whose `lex` (lemma) is in this set.
The lemmas are vocalized (with nikud) since Dicta returns them that
way.

Conservative on purpose: missing entries fall through to top-1, which
is the safe default. Add entries when a real homograph case demands
them, with a unit test.
"""
from __future__ import annotations

FUNCTION_WORD_LEXICON: frozenset[str] = frozenset({
    "אִם",        # whether / if
    "כִּי",       # because / that
    "אֲשֶׁר",     # which / that (relative)
    "שֶׁל",       # of (possessive)
    "אֶת",        # accusative marker
    "אוֹ",        # or
    "אַף",        # also / even (adverbial)
    "אַךְ",       # but / however
    "כְּמוֹ",     # like / as
    "אֲבָל",      # but
    "וְ",         # and (clitic — rarely a standalone lemma)
    "ה",          # definite article (clitic)
})
