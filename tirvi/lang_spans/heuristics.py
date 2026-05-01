"""Heuristic rules over aggregated spans (F16 DE-03/04/05)."""

from tirvi.lang_spans.results import LanguageSpan


def apply_transliteration_rule(
    spans: list[LanguageSpan], text: str
) -> list[LanguageSpan]:
    """DE-03: single-char Latin span flanked by Hebrew → merge into one he span."""
    if len(spans) < 3:
        return list(spans)
    out: list[LanguageSpan] = []
    n = len(spans)
    i = 0
    while i < n:
        if i + 2 < n and _is_translit_triple(spans[i], spans[i + 1], spans[i + 2], text):
            prev, _cur, nxt = spans[i], spans[i + 1], spans[i + 2]
            out.append(LanguageSpan(prev.start, nxt.end, "he", 0.85))
            i += 3
        else:
            out.append(spans[i])
            i += 1
    return out


def _is_translit_triple(
    prev: LanguageSpan, cur: LanguageSpan, nxt: LanguageSpan, text: str
) -> bool:
    return (
        cur.lang == "latin"
        and len(text[cur.start : cur.end]) == 1
        and prev.lang == "he"
        and nxt.lang == "he"
    )


def apply_hyphen_bridge_rule(
    spans: list[LanguageSpan], text: str
) -> list[LanguageSpan]:
    """DE-04: latin-hyphen-latin (no internal WS) → single en span."""
    if len(spans) < 3:
        return list(spans)
    out: list[LanguageSpan] = []
    n = len(spans)
    i = 0
    while i < n:
        if i + 2 < n and _is_hyphen_bridge(spans[i], spans[i + 1], spans[i + 2], text):
            prev, _cur, nxt = spans[i], spans[i + 1], spans[i + 2]
            out.append(LanguageSpan(prev.start, nxt.end, "en", 0.85))
            i += 3
        else:
            out.append(spans[i])
            i += 1
    return out


def _is_hyphen_bridge(
    prev: LanguageSpan, cur: LanguageSpan, nxt: LanguageSpan, text: str
) -> bool:
    return (
        prev.lang == "latin"
        and cur.lang == "symbol"
        and text[cur.start : cur.end] == "-"
        and nxt.lang == "latin"
    )


def apply_num_unification(
    spans: list[LanguageSpan], text: str
) -> list[LanguageSpan]:
    """DE-05: digit/symbol spans collapse into a single num span (conf 1.0)."""
    out: list[LanguageSpan] = []
    for span in spans:
        if span.lang in ("digit", "symbol"):
            _append_num(out, span)
        else:
            out.append(span)
    return out


def _append_num(out: list[LanguageSpan], span: LanguageSpan) -> None:
    if out and out[-1].lang == "num":
        prev = out[-1]
        out[-1] = LanguageSpan(prev.start, span.end, "num", 1.0)
    else:
        out.append(LanguageSpan(span.start, span.end, "num", 1.0))
