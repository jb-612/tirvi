"""F15 T-05 — URL / embedded-acronym skip filter.

Spec: N02/F15 DE-05. AC: US-01/AC-01. FT: FT-negative-2.
"""

import pytest

from tirvi.acronym.expand import tag_and_expand
from tirvi.acronym.skip_filter import should_skip
from tirvi.acronym.value_objects import AcronymEntry, Lexicon
from tirvi.normalize.value_objects import NormalizedText, Span


@pytest.mark.parametrize(
    "token",
    [
        "https://example.com/ד״ר",
        "http://foo.bar",
        "www.example.com",
        "example.com",
        "example.co.il",
    ],
)
def test_should_skip_url_like(token):
    assert should_skip(token) is True


@pytest.mark.parametrize("token", ["ד״ר", "שלום", "ABC", "ת״א."])
def test_should_not_skip_normal_token(token):
    assert should_skip(token) is False


def test_url_token_passes_through_unchanged_no_log():
    lex = Lexicon(
        version="v1",
        entries=(AcronymEntry(form="ד״ר", expansion="דוקטור", source="manual"),),
    )
    nt = NormalizedText(
        text="https://example.com/ד״ר",
        spans=(
            Span(
                text="https://example.com/ד״ר",
                start_char=0,
                end_char=23,
                src_word_indices=(0,),
            ),
        ),
    )
    et = tag_and_expand(nt, lex)
    assert et.spans[0].text == "https://example.com/ד״ר"
    assert et.expansion_log == ()
