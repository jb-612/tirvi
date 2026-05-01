"""F15 T-06 — unknown-acronym fallback (spell_out flag).

Spec: N02/F15 DE-06. AC: US-02/AC-01. FT: FT-110. BT: BT-073.
"""

import pytest

from tirvi.acronym.expand import tag_and_expand
from tirvi.acronym.fallback import is_acronym_candidate
from tirvi.acronym.value_objects import AcronymEntry, Lexicon
from tirvi.normalize.value_objects import NormalizedText, Span


@pytest.mark.parametrize(
    "token",
    ["ד״ר", "ב״הנלד״ץ", "א׳", "AB", "ABCDEF", "USA"],
)
def test_is_acronym_candidate_true(token):
    assert is_acronym_candidate(token) is True


@pytest.mark.parametrize(
    "token",
    ["שלום", "Hello", "A", "ABCDEFG", "abc", "abc.def"],
)
def test_is_acronym_candidate_false(token):
    assert is_acronym_candidate(token) is False


def test_unknown_hebrew_acronym_falls_back_to_spell_out():
    """BT-073 — Yiddish acronym not in lexicon → spell-out."""
    lex = Lexicon(version="v1", entries=())
    nt = NormalizedText(
        text="ב״הנלד״ץ",
        spans=(
            Span(
                text="ב״הנלד״ץ",
                start_char=0,
                end_char=8,
                src_word_indices=(5,),
            ),
        ),
    )
    et = tag_and_expand(nt, lex)
    # Output text keeps the original form (F23 SSML emits per-letter break).
    assert et.spans[0].text == "ב״הנלד״ץ"
    assert len(et.expansion_log) == 1
    log = et.expansion_log[0]
    assert log.original_form == "ב״הנלד״ץ"
    assert log.expansion == "ב״הנלד״ץ"
    assert log.spell_out is True
    assert log.src_word_indices == (5,)


def test_unknown_latin_acronym_falls_back():
    lex = Lexicon(version="v1", entries=())
    nt = NormalizedText(
        text="NASA",
        spans=(Span(text="NASA", start_char=0, end_char=4, src_word_indices=(0,)),),
    )
    et = tag_and_expand(nt, lex)
    assert et.expansion_log[0].spell_out is True
    assert et.expansion_log[0].original_form == "NASA"


def test_lexicon_hit_takes_precedence_over_fallback():
    lex = Lexicon(
        version="v1",
        entries=(AcronymEntry(form="ד״ר", expansion="דוקטור", source="manual"),),
    )
    nt = NormalizedText(
        text="ד״ר",
        spans=(Span(text="ד״ר", start_char=0, end_char=3, src_word_indices=(0,)),),
    )
    et = tag_and_expand(nt, lex)
    assert et.expansion_log[0].spell_out is False
    assert et.spans[0].text == "דוקטור"
