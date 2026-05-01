"""F14 T-06 — repair-log emitter / pipeline composer (DE-06).

Spec: N02/F14 DE-06. AC: US-02/AC-01. FT-anchors: FT-098. BT: BT-066.

Composes the fixed rule order PASS → REJOIN → PUNCT → SPAN → NT (per
``normalize-pipeline.mmd``) and emits a deterministic
``RepairLogEntry`` audit trail sorted by ``(rule_id, position)``.
"""

from __future__ import annotations

from tirvi.results import OCRWord

from .line_break_rejoin import rejoin
from .stray_punct import _is_stray
from .value_objects import NormalizedText, RepairLogEntry, Span

PUNCT_RULE_ID = "stray_punct_drop"


def normalize(words: list[OCRWord]) -> NormalizedText:
    """Apply REJOIN then PUNCT, return a fully-traced :class:`NormalizedText`."""
    if not words:
        return NormalizedText(text="", spans=(), repair_log=())

    rejoined = rejoin(words)
    stray_set = {i for i in range(len(words)) if _is_stray(words, i)}
    return _assemble(words, rejoined, stray_set)


def _drop_entries(
    words: list[OCRWord], span: Span, stray_set: set[int], cursor: int
) -> list[RepairLogEntry]:
    return [
        RepairLogEntry(
            rule_id=PUNCT_RULE_ID, before=words[i].text, after="", position=cursor
        )
        for i in span.src_word_indices
        if i in stray_set
    ]


def _rejoin_entry(
    words: list[OCRWord], span: Span, cursor: int
) -> RepairLogEntry | None:
    if len(span.src_word_indices) <= 1:
        return None
    before = " ".join(words[i].text for i in span.src_word_indices)
    return RepairLogEntry(
        rule_id="line_break_rejoin", before=before, after=span.text, position=cursor
    )


def _assemble(
    words: list[OCRWord],
    rejoined: NormalizedText,
    stray_set: set[int],
) -> NormalizedText:
    final_spans: list[Span] = []
    final_parts: list[str] = []
    log: list[RepairLogEntry] = []
    cursor = 0
    for span in rejoined.spans:
        if any(idx in stray_set for idx in span.src_word_indices):
            log.extend(_drop_entries(words, span, stray_set, cursor))
            continue
        entry = _rejoin_entry(words, span, cursor)
        if entry is not None:
            log.append(entry)
        final_spans.append(
            Span(
                text=span.text,
                start_char=cursor,
                end_char=cursor + len(span.text),
                src_word_indices=span.src_word_indices,
            )
        )
        final_parts.append(span.text)
        cursor += len(span.text) + 1
    log.sort(key=lambda e: (e.rule_id, e.position))
    return NormalizedText(
        text=" ".join(final_parts), spans=tuple(final_spans), repair_log=tuple(log)
    )
