"""F22 T-05 — empty-block handling.

Spec: N02/F22 DE-05. AC: US-01/AC-01. FT-anchors: FT-172.

Per design.md DE-05: "block types with no token (e.g., figure_caption with
no caption text) emit ``tokens=()`` and ``ssml=''``; downstream F23 / F26
short-circuit on empty SSML." F22's job is to **not raise** on such blocks
and to preserve their position in the block list — actual filtering
happens downstream.
"""

from tirvi.blocks import Block
from tirvi.normalize import NormalizedText, Span
from tirvi.plan import ReadingPlan
from tirvi.results import DiacritizationResult, G2PResult, NLPResult, NLPToken


def _inputs_with_one_empty_block() -> dict:
    """3-block page where block b2 has child_word_indices=() (empty)."""
    blocks = (
        Block(
            block_id="b1",
            block_type="heading",
            child_word_indices=(0,),
            bbox=(0, 0, 100, 30),
        ),
        Block(
            block_id="b2",
            block_type="paragraph",
            child_word_indices=(),  # genuine empty block
            bbox=(0, 35, 100, 50),
        ),
        Block(
            block_id="b3",
            block_type="paragraph",
            child_word_indices=(1,),
            bbox=(0, 55, 100, 90),
        ),
    )
    normalized = NormalizedText(
        text="שלום עולם",
        spans=(
            Span(text="שלום", start_char=0, end_char=4, src_word_indices=(0,)),
            Span(text="עולם", start_char=5, end_char=9, src_word_indices=(1,)),
        ),
    )
    nlp = NLPResult(
        provider="dictabert-fake",
        tokens=[
            NLPToken(text="שלום", pos="NOUN", lemma="שלום"),
            NLPToken(text="עולם", pos="NOUN", lemma="עולם"),
        ],
    )
    dia = DiacritizationResult(
        provider="nakdan-fake", diacritized_text="שָׁלוֹם עוֹלָם"
    )
    g2p = G2PResult(provider="phonikud-fake", phonemes=["ʃaˈlom", "oˈlam"])
    return {
        "blocks": blocks,
        "normalized": normalized,
        "nlp": nlp,
        "dia": dia,
        "g2p": g2p,
    }


class TestEmptyBlockSkip:
    def test_us_01_ac_01_ft_172_empty_block_emits_empty_tokens(self) -> None:
        # Given: an F11 block with child_word_indices=()
        # When:  ReadingPlan.from_inputs is called
        # Then:  the corresponding PlanBlock has tokens=() and ssml=""
        i = _inputs_with_one_empty_block()
        plan = ReadingPlan.from_inputs(
            page_id="page-1",
            blocks=i["blocks"],
            normalized=i["normalized"],
            nlp_result=i["nlp"],
            diacritization=i["dia"],
            g2p_result=i["g2p"],
        )
        empty = plan.blocks[1]
        assert empty.block_id == "b2"
        assert empty.tokens == ()
        assert empty.ssml == ""

    def test_us_01_ac_01_ft_172_block_order_preserved_with_empty_block(self) -> None:
        # Given: a 3-block input where the middle block is empty
        # When:  ReadingPlan.from_inputs is called
        # Then:  block order is preserved (no skip / reorder); empty block
        #        stays at position 1
        i = _inputs_with_one_empty_block()
        plan = ReadingPlan.from_inputs(
            page_id="page-1",
            blocks=i["blocks"],
            normalized=i["normalized"],
            nlp_result=i["nlp"],
            diacritization=i["dia"],
            g2p_result=i["g2p"],
        )
        assert [b.block_id for b in plan.blocks] == ["b1", "b2", "b3"]
        assert len(plan.blocks[0].tokens) == 1
        assert len(plan.blocks[1].tokens) == 0
        assert len(plan.blocks[2].tokens) == 1

    def test_us_01_ac_01_from_inputs_does_not_raise_on_empty_block(self) -> None:
        # Given: an empty block exists in the inputs
        # When:  from_inputs is called
        # Then:  no exception is raised (DE-05 — empty-block path is legitimate)
        i = _inputs_with_one_empty_block()
        ReadingPlan.from_inputs(
            page_id="page-1",
            blocks=i["blocks"],
            normalized=i["normalized"],
            nlp_result=i["nlp"],
            diacritization=i["dia"],
            g2p_result=i["g2p"],
        )
