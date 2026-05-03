"""F22 T-02 — ReadingPlan.from_inputs assembly.

Spec: N02/F22 DE-02. AC: US-01/AC-01. FT-anchors: FT-168, FT-173.

The algorithm: walk F11 blocks; for each block, walk normalized spans
whose src_word_indices fall in the block's child_word_indices; build
one PlanToken per span (id = f"{block_id}-{position}"); pull pos/lemma
from NLP, diacritized text from Diac (whitespace-split), ipa from G2P.
"""

from tirvi.blocks import Block
from tirvi.normalize import NormalizedText, Span
from tirvi.plan import PlanBlock, PlanToken, ReadingPlan
from tirvi.results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
    NLPToken,
)


def _make_inputs() -> dict:
    """Build a 2-block / 4-word synthetic page; tokens 1:1 with spans."""
    blocks = (
        Block(
            block_id="b1",
            block_type="heading",
            child_word_indices=(0, 1),
            bbox=(0, 0, 100, 30),
        ),
        Block(
            block_id="b2",
            block_type="paragraph",
            child_word_indices=(2, 3),
            bbox=(0, 40, 100, 70),
        ),
    )
    normalized = NormalizedText(
        text="שלום עולם פרק א",
        spans=(
            Span(text="שלום", start_char=0, end_char=4, src_word_indices=(0,)),
            Span(text="עולם", start_char=5, end_char=9, src_word_indices=(1,)),
            Span(text="פרק", start_char=10, end_char=13, src_word_indices=(2,)),
            Span(text="א", start_char=14, end_char=15, src_word_indices=(3,)),
        ),
    )
    nlp = NLPResult(
        provider="dictabert-fake",
        tokens=[
            NLPToken(text="שלום", pos="NOUN", lemma="שלום"),
            NLPToken(text="עולם", pos="NOUN", lemma="עולם"),
            NLPToken(text="פרק", pos="NOUN", lemma="פרק"),
            NLPToken(text="א", pos="NUM", lemma="א"),
        ],
        confidence=0.9,
    )
    dia = DiacritizationResult(
        provider="nakdan-fake",
        diacritized_text="שָׁלוֹם עוֹלָם פֶּרֶק א",
        confidence=0.85,
    )
    g2p = G2PResult(
        provider="phonikud-fake",
        phonemes=["ʃaˈlom", "oˈlam", "ˈperek", "a"],
        confidence=None,
    )
    return {
        "blocks": blocks,
        "normalized": normalized,
        "nlp": nlp,
        "dia": dia,
        "g2p": g2p,
    }


class TestBuildPlan:
    def test_us_01_ac_01_ft_168_assembles_blocks_from_f11_blocks(self) -> None:
        # Given: 2 F11 blocks + aligned NLP / Diac / G2P inputs
        # When:  ReadingPlan.from_inputs is called
        # Then:  the plan has exactly 2 PlanBlocks, one per F11 block
        i = _make_inputs()
        plan = ReadingPlan.from_inputs(
            page_id="page-1",
            blocks=i["blocks"],
            normalized=i["normalized"],
            nlp_result=i["nlp"],
            diacritization=i["dia"],
            g2p_result=i["g2p"],
        )
        assert isinstance(plan, ReadingPlan)
        assert plan.page_id == "page-1"
        assert len(plan.blocks) == 2
        assert all(isinstance(b, PlanBlock) for b in plan.blocks)
        assert plan.blocks[0].block_id == "b1"
        assert plan.blocks[0].block_kind == "heading"
        assert plan.blocks[1].block_id == "b2"
        assert plan.blocks[1].block_kind == "paragraph"

    def test_us_01_ac_01_ft_168_tokens_carry_lemma_pos_diacritized_ipa(self) -> None:
        # Given: aligned NLP + Diac + G2P inputs
        # When:  ReadingPlan.from_inputs is called
        # Then:  each PlanToken carries pos / lemma / diacritized_text / ipa /
        #        stress from the corresponding upstream result; id matches
        #        f"{block_id}-{position}" per F23 wire-contract pin.
        i = _make_inputs()
        plan = ReadingPlan.from_inputs(
            page_id="page-1",
            blocks=i["blocks"],
            normalized=i["normalized"],
            nlp_result=i["nlp"],
            diacritization=i["dia"],
            g2p_result=i["g2p"],
        )
        # Block 1 ("b1"): tokens for words 0, 1 — שלום and עולם
        b1 = plan.blocks[0]
        assert len(b1.tokens) == 2
        t0, t1 = b1.tokens
        assert isinstance(t0, PlanToken)
        assert t0.id == "b1-0"
        assert t0.text == "שלום"
        assert t0.src_word_indices == (0,)
        assert t0.pos == "NOUN"
        assert t0.lemma == "שלום"
        assert t0.diacritized_text == "שָׁלוֹם"
        # T-07b (cross-feature, F20 → F22): per ADR-028 + F20 design.md HLD
        # Deviations, the per-token PlanToken.ipa is unconditionally None for
        # POC. Whole-text IPA stays on G2PResult.phonemes[0] for F33.
        assert t0.ipa is None
        assert t1.id == "b1-1"
        assert t1.text == "עולם"
        assert t1.diacritized_text == "עוֹלָם"
        # Block 2 ("b2"): tokens for words 2, 3 — פרק and א
        b2 = plan.blocks[1]
        assert len(b2.tokens) == 2
        assert b2.tokens[0].id == "b2-0"
        assert b2.tokens[0].text == "פרק"
        assert b2.tokens[0].pos == "NOUN"
        assert b2.tokens[1].id == "b2-1"
        assert b2.tokens[1].pos == "NUM"

    def test_us_01_ac_01_t_07b_plan_token_ipa_is_none(self) -> None:
        # T-07b (F20 → F22 cross-feature): ADR-028 routes whole-text IPA
        # through G2PResult.phonemes[0]. Per-token PlanToken.ipa is None
        # for POC across every block, regardless of g2p_result content.
        i = _make_inputs()
        plan = ReadingPlan.from_inputs(
            page_id="page-1",
            blocks=i["blocks"],
            normalized=i["normalized"],
            nlp_result=i["nlp"],
            diacritization=i["dia"],
            g2p_result=i["g2p"],
        )
        every_token = [t for b in plan.blocks for t in b.tokens]
        assert every_token  # sanity: non-empty
        assert all(t.ipa is None for t in every_token)

    def test_us_01_ac_01_ft_173_block_order_preserves_rtl(self) -> None:
        # Given: F11 blocks come in RTL reading order (b1 before b2)
        # When:  ReadingPlan.from_inputs is called
        # Then:  block order is preserved (no reordering inside F22)
        i = _make_inputs()
        plan = ReadingPlan.from_inputs(
            page_id="page-1",
            blocks=i["blocks"],
            normalized=i["normalized"],
            nlp_result=i["nlp"],
            diacritization=i["dia"],
            g2p_result=i["g2p"],
        )
        assert [b.block_id for b in plan.blocks] == ["b1", "b2"]
