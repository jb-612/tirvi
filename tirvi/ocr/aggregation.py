"""F10 T-02 — derive top-level lang_hints from per-word values.

OCRResult is a frozen, protected dataclass; rather than extending it with a
top-level ``lang_hints`` field, this helper computes it on demand as the
sorted set-union of per-word ``lang_hint`` values across all pages.
"""

from tirvi.results import OCRResult


def aggregate_lang_hints(result: OCRResult) -> list[str]:
    """Return the sorted, de-duplicated set of per-word lang hints.

    None values are skipped. Result is a sorted list (ASCII order) so output
    is deterministic across runs and platforms.
    """
    seen: set[str] = set()
    for page in result.pages:
        for word in page.words:
            if word.lang_hint is not None:
                seen.add(word.lang_hint)
    return sorted(seen)
