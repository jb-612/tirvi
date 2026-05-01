"""F15 T-04 — tag_and_expand: emit expanded spans + ExpansionLogEntry.

Spec: N02/F15 DE-04. AC: US-01/AC-01. FT: FT-106/107/108. BT: BT-071.
"""

from tirvi.acronym.expand import tag_and_expand
from tirvi.acronym.value_objects import AcronymEntry, Lexicon
from tirvi.normalize.value_objects import NormalizedText, Span


def _lex() -> Lexicon:
    return Lexicon(
        version="2026-05-01",
        entries=(
            AcronymEntry(form="ד״ר", expansion="דוקטור", source="manual"),
            AcronymEntry(form="ת״א", expansion="תל אביב", source="manual"),
        ),
    )


def test_lexicon_hit_emits_expanded_span_and_log_entry():
    lex = _lex()
    nt = NormalizedText(
        text="ד״ר",
        spans=(Span(text="ד״ר", start_char=0, end_char=3, src_word_indices=(0,)),),
    )

    et = tag_and_expand(nt, lex)

    assert et.text == "דוקטור"
    assert len(et.spans) == 1
    assert et.spans[0].text == "דוקטור"
    assert et.spans[0].src_word_indices == (0,)
    assert len(et.expansion_log) == 1
    log = et.expansion_log[0]
    assert log.original_form == "ד״ר"
    assert log.expansion == "דוקטור"
    assert log.src_word_indices == (0,)
    assert log.spell_out is False
    assert et.lexicon_version == "2026-05-01"


def test_multi_word_expansion_forms_one_logical_span():
    lex = _lex()
    nt = NormalizedText(
        text="ת״א",
        spans=(Span(text="ת״א", start_char=0, end_char=3, src_word_indices=(0,)),),
    )

    et = tag_and_expand(nt, lex)

    assert et.text == "תל אביב"
    assert len(et.spans) == 1, "multi-word expansion is one span per DE-04"
    assert et.spans[0].text == "תל אביב"
    assert et.spans[0].src_word_indices == (0,)


def test_trailing_punct_reattaches_to_expansion():
    lex = _lex()
    nt = NormalizedText(
        text="ד״ר?",
        spans=(Span(text="ד״ר?", start_char=0, end_char=4, src_word_indices=(0,)),),
    )

    et = tag_and_expand(nt, lex)
    assert et.text == "דוקטור?"
    assert et.spans[0].text == "דוקטור?"


def test_unknown_token_passes_through_without_log():
    lex = _lex()
    nt = NormalizedText(
        text="שלום",
        spans=(Span(text="שלום", start_char=0, end_char=4, src_word_indices=(0,)),),
    )
    et = tag_and_expand(nt, lex)
    assert et.text == "שלום"
    assert et.spans[0].text == "שלום"
    assert et.expansion_log == ()


def test_multiple_spans_concatenated_with_single_space():
    lex = _lex()
    nt = NormalizedText(
        text="ד״ר כהן",
        spans=(
            Span(text="ד״ר", start_char=0, end_char=3, src_word_indices=(0,)),
            Span(text="כהן", start_char=4, end_char=7, src_word_indices=(1,)),
        ),
    )
    et = tag_and_expand(nt, lex)
    assert et.text == "דוקטור כהן"
    assert et.spans[0].text == "דוקטור"
    assert et.spans[1].text == "כהן"
