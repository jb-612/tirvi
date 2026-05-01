"""F15 T-07 — bbox→span round-trip across expansion (parametrized).

Spec: N02/F15 DE-07. AC: US-01/AC-01. FT: FT-106.

Hand-enumerated table sweeps the input space (lexicon hit, miss,
multi-word, sentence-final punct, URL skip, empty NormalizedText).
Asserts the union of src_word_indices is preserved.
"""

import pytest

from tirvi.acronym.expand import tag_and_expand
from tirvi.acronym.value_objects import AcronymEntry, Lexicon
from tirvi.normalize.value_objects import NormalizedText, Span


_LEX = Lexicon(
    version="v1",
    entries=(
        AcronymEntry(form="ד״ר", expansion="דוקטור", source="manual"),
        AcronymEntry(form="ת״א", expansion="תל אביב", source="manual"),
    ),
)


def _nt(*tokens: tuple[str, int]) -> NormalizedText:
    spans = []
    cursor = 0
    for surface, idx in tokens:
        spans.append(
            Span(
                text=surface,
                start_char=cursor,
                end_char=cursor + len(surface),
                src_word_indices=(idx,),
            )
        )
        cursor += len(surface) + 1
    text = " ".join(s for s, _ in tokens)
    return NormalizedText(text=text, spans=tuple(spans))


@pytest.mark.parametrize(
    "label,nt",
    [
        ("hit", _nt(("ד״ר", 0))),
        ("miss", _nt(("שלום", 0))),
        ("multi-word-expansion", _nt(("ת״א", 0))),
        ("sentence-final-punct", _nt(("ד״ר?", 0))),
        ("url-skip", _nt(("https://x/ד״ר", 0))),
        ("empty", NormalizedText(text="", spans=())),
        ("hit+miss", _nt(("ד״ר", 0), ("כהן", 1))),
        ("fallback-spellout", _nt(("ABC", 7))),
    ],
)
def test_src_word_indices_round_trip(label, nt):
    et = tag_and_expand(nt, _LEX)
    src_in = set()
    for s in nt.spans:
        src_in.update(s.src_word_indices)
    src_out = set()
    for s in et.spans:
        src_out.update(s.src_word_indices)
    assert src_in == src_out, f"row={label}"


@pytest.mark.parametrize(
    "label,nt,expected",
    [
        ("hit-text", _nt(("ד״ר", 0)), "דוקטור"),
        ("miss-text", _nt(("שלום", 0)), "שלום"),
        ("multi-text", _nt(("ת״א", 0)), "תל אביב"),
        ("punct-text", _nt(("ד״ר?", 0)), "דוקטור?"),
    ],
)
def test_output_text_matches_expected(label, nt, expected):
    et = tag_and_expand(nt, _LEX)
    assert et.text == expected, f"row={label}"
