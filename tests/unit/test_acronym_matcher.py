"""F15 T-03 — whole-token matcher + sentence-final punct strip-reattach.

Spec: N02/F15 DE-03. AC: US-01/AC-01. FT: FT-106, FT-107, FT-109.
"""

import pytest

from tirvi.acronym.matcher import match_token
from tirvi.acronym.value_objects import AcronymEntry, Lexicon


@pytest.fixture
def lex() -> Lexicon:
    return Lexicon(
        version="v1",
        entries=(
            AcronymEntry(form="ד״ר", expansion="דוקטור", source="manual"),
            AcronymEntry(form="ת״א", expansion="תל אביב", source="manual"),
        ),
    )


def test_bare_form_match_returns_entry_and_no_trailing_punct(lex):
    res = match_token("ד״ר", lex)
    assert res is not None
    entry, trailing = res
    assert entry.expansion == "דוקטור"
    assert trailing == ""


def test_strips_trailing_period_for_lookup_and_returns_it(lex):
    res = match_token("ד״ר.", lex)
    assert res is not None
    entry, trailing = res
    assert entry.form == "ד״ר"
    assert trailing == "."


@pytest.mark.parametrize("punct", [",", "?", ":", "!", "׃"])
def test_strips_each_supported_trailing_punct(lex, punct):
    res = match_token(f"ד״ר{punct}", lex)
    assert res is not None
    entry, trailing = res
    assert entry.form == "ד״ר"
    assert trailing == punct


def test_ft109_question_mark_after_drhebrew(lex):
    res = match_token("ד״ר?", lex)
    assert res is not None
    entry, trailing = res
    assert entry.expansion == "דוקטור"
    assert trailing == "?"


def test_no_match_returns_none(lex):
    assert match_token("שלום", lex) is None


def test_geresh_and_gershayim_not_stripped(lex):
    # Trailing gershayim is part of an acronym, never stripped.
    assert match_token("ד״", lex) is None  # not a known form, untouched


def test_multiple_trailing_punct_all_reattached(lex):
    res = match_token("ד״ר?!", lex)
    assert res is not None
    entry, trailing = res
    assert entry.form == "ד״ר"
    assert trailing == "?!"
