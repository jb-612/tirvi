"""F23 T-02 — per-token <mark> emission with XML-escaped surface text.

Spec: N02/F23 DE-02. AC: US-01/AC-01. FT-anchors: FT-174.

Each PlanToken gets a ``<mark name="{token.id}"/>`` immediately
preceding its escaped surface form. Mark names are wire-pinned to
PlanToken.id (``{block_id}-{position}``) — same shape consumed by
F26 / F30 / F35.
"""

from xml.etree import ElementTree as ET

from tirvi.plan import PlanBlock, PlanToken
from tirvi.ssml import build_block_ssml


def _block(*tokens: PlanToken) -> PlanBlock:
    return PlanBlock(block_id="b1", block_type="paragraph", tokens=tokens)


class TestPerWordMark:
    def test_us_01_ac_01_ft_174_every_token_gets_mark_pre_emit(self) -> None:
        block = _block(
            PlanToken(id="b1-0", text="שלום", src_word_indices=(0,)),
            PlanToken(id="b1-1", text="עולם", src_word_indices=(1,)),
            PlanToken(id="b1-2", text="פרק", src_word_indices=(2,)),
        )
        out = build_block_ssml(block)
        root = ET.fromstring(out)
        marks = root.findall("mark")
        assert len(marks) == 3

    def test_us_01_ac_01_ft_174_mark_name_is_plan_token_id(self) -> None:
        block = _block(
            PlanToken(id="b1-0", text="א", src_word_indices=(0,)),
            PlanToken(id="b1-1", text="ב", src_word_indices=(1,)),
        )
        out = build_block_ssml(block)
        root = ET.fromstring(out)
        names = [m.get("name") for m in root.findall("mark")]
        assert names == ["b1-0", "b1-1"]

    def test_us_01_ac_01_ft_174_mark_immediately_precedes_surface_text(self) -> None:
        # Each mark's tail (the text content after the element) is the
        # surface form for that token.
        block = _block(
            PlanToken(
                id="b1-0",
                text="שלום",
                src_word_indices=(0,),
                diacritized_text="שָׁלוֹם",
            ),
        )
        out = build_block_ssml(block)
        root = ET.fromstring(out)
        mark = root.findall("mark")[0]
        assert mark.tail is not None
        assert "שָׁלוֹם" in mark.tail

    def test_us_01_ac_01_ft_174_mark_count_equals_token_count(self) -> None:
        for n in (0, 1, 5, 20):
            tokens = tuple(
                PlanToken(id=f"b1-{i}", text="א", src_word_indices=(i,))
                for i in range(n)
            )
            out = build_block_ssml(_block(*tokens))
            root = ET.fromstring(out)
            assert len(root.findall("mark")) == n

    def test_us_01_ac_01_token_text_with_xml_specials_is_escaped(self) -> None:
        # An ampersand in surface text would break the SSML parse without escape
        block = _block(
            PlanToken(id="b1-0", text="A & B", src_word_indices=(0,)),
        )
        out = build_block_ssml(block)
        # Escaped output must parse cleanly
        root = ET.fromstring(out)
        mark = root.findall("mark")[0]
        # ElementTree decodes the entity back to literal "&" in .tail
        assert mark.tail is not None
        assert "A & B" in mark.tail

    def test_us_01_ac_01_token_text_with_lt_gt_does_not_break_parse(self) -> None:
        block = _block(
            PlanToken(id="b1-0", text="a < b > c", src_word_indices=(0,)),
        )
        out = build_block_ssml(block)
        root = ET.fromstring(out)
        mark = root.findall("mark")[0]
        assert mark.tail is not None
        assert "a < b > c" in mark.tail
