"""F14 T-04 — stray-punctuation drop rule (DE-04).

Spec: N02/F14 DE-04. AC: US-02/AC-01. FT-anchors: FT-096. BT: BT-064.

Drops a word if and only if:
  - ``conf is not None and conf < 0.4``, AND
  - text is exactly U+002C (``,``) or U+0027 (``'``), AND
  - no neighbouring word shares its line (``y`` overlap).

Hebrew geresh (U+05F3) and gershayim (U+05F4) are explicitly preserved
even at low confidence — they collide visually with ASCII apostrophe in
many fonts but encode acronym structure (e.g. ``מס׳``, ``ת״א``).
"""

from __future__ import annotations

from tirvi.results import OCRWord

from .value_objects import NormalizedText, RepairLogEntry, Span

RULE_ID = "stray_punct_drop"
CONF_THRESHOLD = 0.4
DROPPABLE = (",", "'")  # U+002C, U+0027 — ASCII only


def _shares_line(a: OCRWord, b: OCRWord) -> bool:
    return a.bbox[1] <= b.bbox[3] and b.bbox[1] <= a.bbox[3]


def _has_same_line_neighbour(words: list[OCRWord], idx: int) -> bool:
    target = words[idx]
    for j, other in enumerate(words):
        if j == idx:
            continue
        if _shares_line(target, other):
            return True
    return False


def _is_stray(words: list[OCRWord], idx: int) -> bool:
    word = words[idx]
    if word.conf is None or word.conf >= CONF_THRESHOLD:
        return False
    if word.text not in DROPPABLE:
        return False
    return not _has_same_line_neighbour(words, idx)


def drop_stray_punct(words: list[OCRWord]) -> NormalizedText:
    """Apply the stray-punctuation drop rule to ``words``."""
    if not words:
        return NormalizedText(text="", spans=(), repair_log=())

    keep_indices = [i for i in range(len(words)) if not _is_stray(words, i)]
    drop_indices = [i for i in range(len(words)) if i not in keep_indices]
    return _build_result(words, keep_indices, drop_indices)


def _build_result(
    words: list[OCRWord],
    keep_indices: list[int],
    drop_indices: list[int],
) -> NormalizedText:
    spans: list[Span] = []
    parts: list[str] = []
    cursor = 0
    for i in keep_indices:
        text = words[i].text
        spans.append(
            Span(
                text=text,
                start_char=cursor,
                end_char=cursor + len(text),
                src_word_indices=(i,),
            )
        )
        parts.append(text)
        cursor += len(text) + 1
    repair_log = tuple(
        RepairLogEntry(rule_id=RULE_ID, before=words[i].text, after="", position=0)
        for i in drop_indices
    )
    return NormalizedText(
        text=" ".join(parts), spans=tuple(spans), repair_log=repair_log
    )
