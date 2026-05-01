"""F15 — Acronym tag-and-expand pass.

Spec: N02/F15 DE-04..DE-08.
"""

from __future__ import annotations

from tirvi.acronym.matcher import match_token
from tirvi.acronym.skip_filter import should_skip
from tirvi.acronym.fallback import is_acronym_candidate
from tirvi.acronym.value_objects import (
    ExpandedText,
    ExpansionLogEntry,
    Lexicon,
)
from tirvi.normalize.value_objects import NormalizedText, Span


def tag_and_expand(text: NormalizedText, lexicon: Lexicon) -> ExpandedText:
    """Walk ``text.spans`` and emit acronym-expanded spans + log."""
    out_spans: list[Span] = []
    out_logs: list[ExpansionLogEntry] = []
    cursor = 0
    parts: list[str] = []

    for span in text.spans:
        new_text, log = _expand_span(span, lexicon)
        if log is not None:
            out_logs.append(log)
        if parts:
            cursor += 1  # the joining space
        out_spans.append(
            Span(
                text=new_text,
                start_char=cursor,
                end_char=cursor + len(new_text),
                src_word_indices=span.src_word_indices,
            )
        )
        cursor += len(new_text)
        parts.append(new_text)

    return ExpandedText(
        text=" ".join(parts),
        spans=tuple(out_spans),
        repair_log=text.repair_log,
        expansion_log=tuple(out_logs),
        lexicon_version=lexicon.version,
    )


def _expand_span(
    span: Span, lexicon: Lexicon
) -> tuple[str, ExpansionLogEntry | None]:
    """Return (output_surface, log_entry_or_none) for a single span."""
    surface = span.text
    if should_skip(surface):
        return surface, None
    hit = match_token(surface, lexicon)
    if hit is not None:
        entry, trailing = hit
        new = entry.expansion + trailing
        log = ExpansionLogEntry(
            original_form=entry.form,
            expansion=entry.expansion,
            src_word_indices=span.src_word_indices,
            spell_out=False,
        )
        return new, log
    if is_acronym_candidate(surface):
        log = ExpansionLogEntry(
            original_form=surface,
            expansion=surface,
            src_word_indices=span.src_word_indices,
            spell_out=True,
        )
        return surface, log
    return surface, None
