"""F22 — ReadingPlan aggregate root.

Spec: N02/F22 DE-01, DE-04, DE-06, DE-07. AC: US-01/AC-01, US-02/AC-01.
"""

from dataclasses import dataclass
from typing import Any

from tirvi.blocks import Block
from tirvi.normalize import NormalizedText, Span
from tirvi.results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
)

from .value_objects import PlanBlock, PlanToken


@dataclass(frozen=True)
class ReadingPlan:
    """Page-level reading-plan aggregate.

    Invariants (named, TDD fills):
      - INV-PLAN-001 (DE-04): every PlanToken.id is unique across blocks
      - INV-PLAN-002 (DE-04): block order matches reading order (RTL-corrected)
      - INV-PLAN-003 (DE-06): ``to_json()`` is byte-identical across runs (sort_keys, NFC)
      - INV-PLAN-004 (DE-07): ``to_page_json(ocr_result)`` conforms to
        ``docs/schemas/page.schema.json``
    """

    page_id: str
    blocks: tuple[PlanBlock, ...]

    @classmethod
    def from_inputs(
        cls,
        page_id: str,
        blocks: tuple[Block, ...],
        normalized: NormalizedText,
        nlp_result: NLPResult,
        diacritization: DiacritizationResult,
        g2p_result: G2PResult,
    ) -> "ReadingPlan":
        """Assemble a ReadingPlan from F11 blocks + aligned NLP / Diac / G2P inputs.

        Token alignment: ``normalized.spans``, ``nlp_result.tokens``,
        ``g2p_result.phonemes``, and the whitespace-split of
        ``diacritization.diacritized_text`` are all index-aligned at the
        global (page-wide) level. Each span belongs to exactly one F11
        block, identified by the membership of its ``src_word_indices``
        in the block's ``child_word_indices``. (T-02, FT-168, FT-173.)
        """
        diacritized_words = diacritization.diacritized_text.split()
        plan_blocks = tuple(
            _build_plan_block(
                block,
                normalized.spans,
                nlp_result,
                diacritized_words,
                g2p_result,
            )
            for block in blocks
        )
        return cls(page_id=page_id, blocks=plan_blocks)

    def to_json(self) -> str:
        # TODO US-01/AC-01 (T-06, INV-PLAN-003): json.dumps(asdict(self),
        #                        sort_keys=True, ensure_ascii=False, indent=2)
        raise NotImplementedError

    def to_page_json(self, ocr_result: Any) -> dict[str, Any]:
        # TODO US-01/AC-01 (T-07, post-review C4, INV-PLAN-004): build
        #                        {page_image_url, words[], marks_to_word_index}
        # TODO words[].bbox from ocr_result; marks_to_word_index =
        #                        {token.id: first(token.src_word_indices)}
        raise NotImplementedError


def _build_plan_block(
    block: Block,
    spans: tuple[Span, ...],
    nlp_result: NLPResult,
    diacritized_words: list[str],
    g2p_result: G2PResult,
) -> PlanBlock:
    """Build one PlanBlock from its F11 Block and the page-global token streams."""
    block_words = set(block.child_word_indices)
    member_pairs = [
        (i, span)
        for i, span in enumerate(spans)
        if all(w in block_words for w in span.src_word_indices)
    ]
    tokens = tuple(
        _build_plan_token(
            block_id=block.block_id,
            position=local_pos,
            global_idx=global_idx,
            span=span,
            nlp_result=nlp_result,
            diacritized_words=diacritized_words,
            g2p_result=g2p_result,
        )
        for local_pos, (global_idx, span) in enumerate(member_pairs)
    )
    return PlanBlock(
        block_id=block.block_id,
        block_type=block.block_type,
        tokens=tokens,
        bbox=block.bbox,
    )


def _build_plan_token(
    *,
    block_id: str,
    position: int,
    global_idx: int,
    span: Span,
    nlp_result: NLPResult,
    diacritized_words: list[str],
    g2p_result: G2PResult,
) -> PlanToken:
    """Build one PlanToken; id format ``{block_id}-{position}`` per INV-PLAN-T-001."""
    nlp_token = nlp_result.tokens[global_idx] if global_idx < len(nlp_result.tokens) else None
    diacritized = (
        diacritized_words[global_idx] if global_idx < len(diacritized_words) else None
    )
    ipa = g2p_result.phonemes[global_idx] if global_idx < len(g2p_result.phonemes) else None
    return PlanToken(
        id=f"{block_id}-{position}",
        text=span.text,
        src_word_indices=span.src_word_indices,
        pos=nlp_token.pos if nlp_token is not None else None,
        lemma=nlp_token.lemma if nlp_token is not None else None,
        diacritized_text=diacritized,
        ipa=ipa,
        stress=None,
    )
