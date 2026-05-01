"""Top-level detect_language_spans pipeline (F16 DE-06/07)."""

from tirvi.lang_spans.aggregate import aggregate_runs
from tirvi.lang_spans.classify import classify_char
from tirvi.lang_spans.heuristics import (
    apply_hyphen_bridge_rule,
    apply_num_unification,
    apply_transliteration_rule,
)
from tirvi.lang_spans.results import LanguageSpan, LanguageSpansResult


def detect_language_spans(text: str) -> LanguageSpansResult:
    tags = [classify_char(c) for c in text]
    spans = aggregate_runs(tags, text)
    spans = apply_transliteration_rule(spans, text)
    spans = apply_hyphen_bridge_rule(spans, text)
    spans = apply_num_unification(spans, text)
    spans = [_finalize(s) for s in spans]
    confidence = min((s.confidence for s in spans), default=None)
    return LanguageSpansResult(
        spans=tuple(spans),
        provider="tirvi-rules-v1",
        confidence=confidence,
    )


def _finalize(span: LanguageSpan) -> LanguageSpan:
    if span.lang == "latin":
        return LanguageSpan(span.start, span.end, "en", span.confidence)
    return span
