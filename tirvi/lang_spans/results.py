"""LanguageSpan + LanguageSpansResult value types (F16 DE-06)."""

from dataclasses import dataclass
from typing import Literal

LangTag = Literal["he", "en", "num"]


@dataclass(frozen=True)
class LanguageSpan:
    """Half-open span [start, end) tagged with a language."""

    start: int
    end: int
    lang: str
    confidence: float


@dataclass(frozen=True)
class LanguageSpansResult:
    """Output of :func:`tirvi.lang_spans.detect_language_spans` (F16 DE-06)."""

    spans: tuple[LanguageSpan, ...]
    provider: str = "tirvi-rules-v1"
    confidence: float | None = None
