"""F14 T-03 — line-break rejoin rule (DE-03).

Spec: N02/F14 DE-03. AC: US-01/AC-01. FT-anchors: FT-094, FT-095. BT: BT-063.

Detects mid-word line breaks and fuses two consecutive ``OCRWord`` items
when separated by a y-delta greater than the median word height and the
trailing word lacks sentence-final punctuation and a mid-token hyphen.
"""

from __future__ import annotations

from statistics import median

from tirvi.results import OCRWord

from .value_objects import NormalizedText, RepairLogEntry, Span

RULE_ID = "line_break_rejoin"
SENTENCE_FINAL = (".", ",", "?", ":", "!")


def _word_height(word: OCRWord) -> int:
    _, y0, _, y1 = word.bbox
    return y1 - y0


def _is_line_break(prev: OCRWord, curr: OCRWord, line_height_median: float) -> bool:
    return (curr.bbox[1] - prev.bbox[1]) > line_height_median


def _is_lone_punct(text: str) -> bool:
    return len(text) == 1 and text in SENTENCE_FINAL + ("'",)


def _should_rejoin(prev: OCRWord, curr: OCRWord, line_height_median: float) -> bool:
    if not _is_line_break(prev, curr, line_height_median):
        return False
    if prev.text.endswith(SENTENCE_FINAL) or "-" in prev.text:
        return False
    return not _is_lone_punct(curr.text)


def rejoin(words: list[OCRWord]) -> NormalizedText:
    """Apply the line-break rejoin rule across ``words``.

    Returns a :class:`NormalizedText` whose spans either preserve a single
    source word index (no rejoin) or fuse two adjacent indices (rejoin).
    """
    if not words:
        return NormalizedText(text="", spans=(), repair_log=())

    heights = [_word_height(w) for w in words]
    line_height_median = median(heights) if heights else 0.0

    groups = _group_indices(words, line_height_median)
    return _build_result(words, groups)


def _group_indices(
    words: list[OCRWord], line_height_median: float
) -> list[tuple[int, ...]]:
    groups: list[list[int]] = [[0]]
    for i in range(1, len(words)):
        if _should_rejoin(words[i - 1], words[i], line_height_median):
            groups[-1].append(i)
        else:
            groups.append([i])
    return [tuple(g) for g in groups]


def _build_result(
    words: list[OCRWord], groups: list[tuple[int, ...]]
) -> NormalizedText:
    spans: list[Span] = []
    repair_log: list[RepairLogEntry] = []
    parts: list[str] = []
    cursor = 0
    for group in groups:
        text = "".join(words[i].text for i in group)
        spans.append(
            Span(
                text=text,
                start_char=cursor,
                end_char=cursor + len(text),
                src_word_indices=group,
            )
        )
        if len(group) > 1:
            before = " ".join(words[i].text for i in group)
            repair_log.append(
                RepairLogEntry(
                    rule_id=RULE_ID, before=before, after=text, position=cursor
                )
            )
        parts.append(text)
        cursor += len(text) + 1
    return NormalizedText(
        text=" ".join(parts), spans=tuple(spans), repair_log=tuple(repair_log)
    )
