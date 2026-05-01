"""Post-OCR Hebrew character correction.

Two-stage strategy:
  1. Hardcoded substitution table for high-frequency exam words where the
     Nakdan word-list heuristic fails (Nakdan accepts both ם/ס forms).
  2. Heuristic: query Nakdan, swap ס→ם / ו→ן when the original is rejected
     and the substitute is accepted.
"""
from __future__ import annotations

# High-frequency words Tesseract heb_best confuses ס↔ם. Both forms are valid
# Hebrew (Nakdan accepts both) so the word-list heuristic alone fails.
# All entries are cases where the ם form is overwhelmingly more common in
# educational/exam text (>1000:1 frequency ratio in HeWaC).
_KNOWN_OCR_FIXES: dict[str, str] = {
    # ם/ס confusions
    "גורס":   "גורם",      # cause/factor (noun, verb)
    "תגרוס":  "תגרום",     # will cause (2nd/3rd-fem-sing fut)
    "אינס":   "אינם",      # are not (3rd-masc-pl neg)
    "סיוס":   "סיום",      # ending/conclusion
    "מקוס":   "מקום",      # place
    "אדס":    "אדם",      # person
    "יוס":    "יום",       # day
    "עולס":   "עולם",      # world
    "שלוס":   "שלום",      # peace, hello
    "שס":     "שם",        # there, name
    "סוס":    "סום",       # (rare; usually horse — but keep override out)
    "פעמיס":  "פעמים",     # times
    "אנשיס":  "אנשים",     # people
    "דבריס":  "דברים",     # things
    "אומריס": "אומרים",    # they say
    # ו/ן confusions (less common but worth catching)
    "מאו":    "מאן",       # (rare)
}
# Remove the questionable "סוס" override — actually a real word (horse)
del _KNOWN_OCR_FIXES["סוס"]

_FINAL_SUBS: list[tuple[str, str]] = [
    ("ס", "ם"),
    ("ו", "ן"),
]


def correct_final_letters(words: list[str]) -> list[str]:
    """Apply hardcoded fixes first, then Nakdan-heuristic for unknown words."""
    # Stage 1: hardcoded high-frequency substitutions
    words = [_KNOWN_OCR_FIXES.get(w, w) for w in words]
    # Stage 2: Nakdan-heuristic for remaining suspicious words
    suspects = [w for w in words if _suspicious(w)]
    if not suspects:
        return words
    fixes = {w: _fix(w) for w in suspects}
    return [fixes.get(w, w) for w in words]


def _suspicious(word: str) -> bool:
    return bool(word) and word[-1] in {s for s, _ in _FINAL_SUBS}


def _fix(word: str) -> str:
    try:
        if not _nakdan_rejects(word):
            return word
        for wrong, correct in _FINAL_SUBS:
            if word.endswith(wrong):
                candidate = word[:-1] + correct
                if not _nakdan_rejects(candidate):
                    return candidate
    except Exception:
        pass
    return word


def _nakdan_rejects(word: str) -> bool:
    try:
        from tirvi.adapters.nakdan.client import diacritize_via_api
        entries = diacritize_via_api(word)
        for entry in entries:
            if not entry.get("sep"):
                return bool(entry.get("fnotfromwl"))
        return False
    except Exception:
        return False
