"""Post-OCR Hebrew character correction.

Uses the Nakdan REST API word-list flag as oracle: if a word is not in
Nakdan's lexicon but the substituted form is, apply the correction.
"""
from __future__ import annotations

_FINAL_SUBS: list[tuple[str, str]] = [
    ("ס", "ם"),
    ("ו", "ן"),
]


def correct_final_letters(words: list[str]) -> list[str]:
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
