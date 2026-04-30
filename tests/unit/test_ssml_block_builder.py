"""F23 T-01 — per-block SSML <speak> document builder.

Spec: N02/F23 DE-01, DE-02. AC: US-01/AC-01.

``build_block_ssml(block)`` wraps the block's tokens in a
``<speak xml:lang="he-IL">`` document with a ``<mark name="{token.id}"/>``
preceding each token's surface form. Mark format pinned to PlanToken.id
per F23 HLD-deviation note (`{block_id}-{position}`); same string flows
through F26 / F30 / F35 unchanged.
"""

from tirvi.plan import PlanBlock, PlanToken
from tirvi.ssml import build_block_ssml


def _block() -> PlanBlock:
    return PlanBlock(
        block_id="b1",
        block_type="heading",
        tokens=(
            PlanToken(
                id="b1-0",
                text="שלום",
                src_word_indices=(0,),
                diacritized_text="שָׁלוֹם",
            ),
            PlanToken(
                id="b1-1",
                text="עולם",
                src_word_indices=(1,),
                diacritized_text="עוֹלָם",
            ),
        ),
    )


class TestSSMLBlockBuilder:
    def test_us_01_ac_01_returns_string(self) -> None:
        out = build_block_ssml(_block())
        assert isinstance(out, str)
        assert len(out) > 0

    def test_us_01_ac_01_wraps_in_speak_with_xml_lang_he_il(self) -> None:
        # INV-SSML-001 (DE-01): <speak xml:lang="he-IL"> wrapper
        out = build_block_ssml(_block())
        assert out.startswith('<speak xml:lang="he-IL">')
        assert out.endswith("</speak>")

    def test_us_01_ac_01_emits_mark_per_token_with_plan_token_id(self) -> None:
        # INV-SSML-002 (DE-02): every token gets <mark name="{token.id}"/>
        # INV-SSML-005 (F23 HLD-deviation): mark format {block_id}-{position}
        out = build_block_ssml(_block())
        assert '<mark name="b1-0"/>' in out
        assert '<mark name="b1-1"/>' in out

    def test_us_01_ac_01_mark_count_equals_token_count(self) -> None:
        out = build_block_ssml(_block())
        assert out.count("<mark") == 2

    def test_us_01_ac_01_emits_diacritized_text_when_available(self) -> None:
        # The vocalized form drives Wavenet's pronunciation; raw text is fallback
        out = build_block_ssml(_block())
        assert "שָׁלוֹם" in out
        assert "עוֹלָם" in out

    def test_us_01_ac_01_falls_back_to_raw_text_when_diacritized_missing(self) -> None:
        block = PlanBlock(
            block_id="b9",
            block_type="paragraph",
            tokens=(
                PlanToken(id="b9-0", text="abc", src_word_indices=(0,)),  # no diacritized
            ),
        )
        out = build_block_ssml(block)
        assert "abc" in out

    def test_us_01_ac_01_empty_block_produces_minimal_speak(self) -> None:
        # An empty block (DE-05 path) still produces a well-formed <speak>
        empty = PlanBlock(block_id="b1", block_type="heading", tokens=())
        out = build_block_ssml(empty)
        assert out == '<speak xml:lang="he-IL"></speak>'
