"""F14 T-01 — pure pass-through normalization (POC numbering).

Spec: N02/F14 DE-02. AC: US-01/AC-01. FT-anchors: FT-094.

Joins OCR words by single spaces, emitting one :class:`Span` per word that
records its character range and source word index. No repair rules apply
in the POC pass-through path; ``repair_log`` is empty. Hebrew NFD nikud is
preserved (no NFC).
"""

from __future__ import annotations

from tirvi.results import OCRWord

from .value_objects import NormalizedText, Span


def normalize_text(words: list[OCRWord]) -> NormalizedText:
    """Pass-through join: ``" ".join(w.text for w in words)``.

    Each input word produces one :class:`Span` covering ``[start_char, end_char)``
    and tracing back via ``src_word_indices=(i,)``.
    """
    if not words:
        return NormalizedText(text="", spans=(), repair_log=())
    spans: list[Span] = []
    cursor = 0
    parts: list[str] = []
    for i, word in enumerate(words):
        text = word.text
        spans.append(
            Span(
                text=text,
                start_char=cursor,
                end_char=cursor + len(text),
                src_word_indices=(i,),
            )
        )
        parts.append(text)
        cursor += len(text) + 1  # +1 for the joining space
    return NormalizedText(
        text=" ".join(parts),
        spans=tuple(spans),
        repair_log=(),
    )
