"""Run-length aggregation with whitespace absorption (F16 DE-02)."""

from tirvi.lang_spans.classify import Script
from tirvi.lang_spans.results import LanguageSpan

_BOUNDARY = (Script.WS, Script.OTHER)
_LANG_OF: dict[Script, str] = {
    Script.HE: "he",
    Script.LATIN: "latin",
    Script.DIGIT: "digit",
    Script.SYMBOL: "symbol",
}


def _raw_runs(tags: list[Script]) -> list[tuple[int, int, Script]]:
    runs: list[tuple[int, int, Script]] = []
    i = 0
    n = len(tags)
    while i < n:
        j = i + 1
        while j < n and tags[j] == tags[i]:
            j += 1
        runs.append((i, j, tags[i]))
        i = j
    return runs


def aggregate_runs(tags: list[Script], text: str) -> list[LanguageSpan]:
    spans: list[LanguageSpan] = []
    for start, end, script in _raw_runs(tags):
        if script in _BOUNDARY:
            if spans:
                spans[-1] = _extend(spans[-1], end)
            continue
        lang = _LANG_OF[script]
        if spans and spans[-1].lang == lang:
            spans[-1] = _extend(spans[-1], end)
        else:
            spans.append(LanguageSpan(start=start, end=end, lang=lang, confidence=1.0))
    return spans


def _extend(span: LanguageSpan, new_end: int) -> LanguageSpan:
    return LanguageSpan(
        start=span.start, end=new_end, lang=span.lang, confidence=span.confidence
    )
