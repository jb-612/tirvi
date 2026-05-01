"""F22 — ReadingPlan aggregate root.

Spec: N02/F22 DE-01, DE-04, DE-06, DE-07. AC: US-01/AC-01, US-02/AC-01.
"""

import json
from dataclasses import asdict, dataclass
from typing import Any

from tirvi.blocks import Block
from tirvi.normalize import NormalizedText, Span
from tirvi.results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
    OCRResult,
    OCRWord,
)

from .value_objects import PROVENANCE_MISSING, PlanBlock, PlanToken


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
        """Serialize the plan to deterministic JSON (T-06, INV-PLAN-003).

        Two runs over the same input produce byte-identical bytes — the
        basis for the ``drafts/<reading-plan-sha>/`` content-hash
        directory in PLAN-POC.md.
        """
        return json.dumps(
            asdict(self),
            sort_keys=True,
            ensure_ascii=False,
            indent=2,
        )

    def to_page_json(
        self,
        ocr_result: OCRResult,
        page_image_url: str = "page-1.png",
    ) -> dict[str, Any]:
        """F35-consumed page projection (T-07, post-review C4, INV-PLAN-004).

        Conforms to ``docs/schemas/page.schema.json``. POC reads only the
        first OCR page (single-page demo). Bboxes convert from
        OCRWord's ``(x0, y0, x1, y1)`` to schema's ``[x, y, w, h]``.
        ``marks_to_word_index`` maps each token's stable id to its
        first source word index.
        """
        page = ocr_result.pages[0]
        return {
            "page_image_url": page_image_url,
            "words": [_word_to_schema_dict(w) for w in page.words],
            "marks_to_word_index": _build_marks_to_word_index(self.blocks),
        }


def _word_to_schema_dict(word: OCRWord) -> dict[str, Any]:
    """Convert an OCRWord to the page.schema.json word shape.

    OCRWord.bbox is ``(x0, y0, x1, y1)`` per INV-OCR-W-001; the schema
    wants ``[x, y, w, h]``. The conversion: w = x1 - x0; h = y1 - y0.
    """
    x0, y0, x1, y1 = word.bbox
    return {
        "text": word.text,
        "bbox": [x0, y0, x1 - x0, y1 - y0],
        "lang_hint": word.lang_hint,
    }


def _build_marks_to_word_index(blocks: tuple[PlanBlock, ...]) -> dict[str, int]:
    """Map each PlanToken.id to its first src_word_index across all blocks."""
    return {
        token.id: token.src_word_indices[0]
        for block in blocks
        for token in block.tokens
        if token.src_word_indices
    }


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
    # T-07b (F20 ADR-028): whole-text IPA lives on G2PResult.phonemes[0] for
    # F33; per-token PlanToken.ipa is unconditionally None for POC. The
    # ``g2p_result`` argument stays in the signature so F22's call sites
    # remain stable when per-token IPA returns post-POC.
    del g2p_result
    pos = nlp_token.pos if nlp_token is not None else None
    lemma = nlp_token.lemma if nlp_token is not None else None
    return PlanToken(
        id=f"{block_id}-{position}",
        text=span.text,
        src_word_indices=span.src_word_indices,
        pos=pos,
        lemma=lemma,
        diacritized_text=diacritized,
        ipa=None,
        stress=None,
        provenance=_build_provenance(pos=pos, lemma=lemma, vocalized=diacritized),
    )


def _build_provenance(
    *,
    pos: str | None,
    lemma: str | None,
    vocalized: str | None,
) -> dict[str, str]:
    """Build the DE-03 provenance dict; absent inputs become ``"missing"``."""
    return {
        "pos": pos if pos is not None else PROVENANCE_MISSING,
        "lemma": lemma if lemma is not None else PROVENANCE_MISSING,
        "morph": PROVENANCE_MISSING,
        "ipa": PROVENANCE_MISSING,
        "stress": PROVENANCE_MISSING,
        "vocalized": vocalized if vocalized is not None else PROVENANCE_MISSING,
    }
