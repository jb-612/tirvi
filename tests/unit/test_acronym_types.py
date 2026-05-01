"""F15 T-01 — Acronym value types.

Spec: N02/F15 DE-01. AC: US-01/AC-01, US-02/AC-01.
"""

from dataclasses import FrozenInstanceError

import pytest

from tirvi.acronym.value_objects import (
    AcronymEntry,
    ExpandedText,
    ExpansionLogEntry,
    Lexicon,
)
from tirvi.normalize.value_objects import RepairLogEntry, Span


def test_acronym_entry_is_frozen_with_default_context_tags():
    entry = AcronymEntry(form="ד״ר", expansion="דוקטור", source="manual")

    assert entry.form == "ד״ר"
    assert entry.expansion == "דוקטור"
    assert entry.source == "manual"
    assert entry.context_tags == ()

    with pytest.raises(FrozenInstanceError):
        entry.form = "אחר"  # type: ignore[misc]


def test_acronym_entry_accepts_context_tags_tuple():
    entry = AcronymEntry(
        form="ת״א",
        expansion="תל אביב",
        source="manual",
        context_tags=("geo",),
    )
    assert entry.context_tags == ("geo",)


def test_lexicon_indexes_entries_by_form_in_post_init():
    e1 = AcronymEntry(form="ד״ר", expansion="דוקטור", source="manual")
    e2 = AcronymEntry(form="ת״א", expansion="תל אביב", source="manual")
    lex = Lexicon(version="2026-05-01", entries=(e1, e2))

    assert lex._index["ד״ר"] is e1
    assert lex._index["ת״א"] is e2


def test_lexicon_is_frozen():
    lex = Lexicon(version="v1", entries=())
    with pytest.raises(FrozenInstanceError):
        lex.version = "v2"  # type: ignore[misc]


def test_expansion_log_entry_carries_traceability_fields():
    le = ExpansionLogEntry(
        original_form="ד״ר",
        expansion="דוקטור",
        src_word_indices=(3,),
        spell_out=False,
    )
    assert le.original_form == "ד״ר"
    assert le.expansion == "דוקטור"
    assert le.src_word_indices == (3,)
    assert le.spell_out is False


def test_expanded_text_holds_spans_logs_and_lexicon_version():
    span = Span(text="דוקטור", start_char=0, end_char=6, src_word_indices=(0,))
    le = ExpansionLogEntry(
        original_form="ד״ר",
        expansion="דוקטור",
        src_word_indices=(0,),
        spell_out=False,
    )
    repair = RepairLogEntry(rule_id="X", before="a", after="b", position=0)
    et = ExpandedText(
        text="דוקטור",
        spans=(span,),
        repair_log=(repair,),
        expansion_log=(le,),
        lexicon_version="2026-05-01",
    )
    assert et.text == "דוקטור"
    assert et.spans == (span,)
    assert et.repair_log == (repair,)
    assert et.expansion_log == (le,)
    assert et.lexicon_version == "2026-05-01"
