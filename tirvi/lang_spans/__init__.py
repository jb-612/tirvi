"""F16 — mixed-language run detection (Hebrew / English / Numeric)."""

from tirvi.lang_spans.detect import detect_language_spans
from tirvi.lang_spans.results import LanguageSpan, LanguageSpansResult

__all__ = ["LanguageSpan", "LanguageSpansResult", "detect_language_spans"]
