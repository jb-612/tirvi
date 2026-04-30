"""F22 — ReadingPlan aggregate root.

Spec: N02/F22 DE-01, DE-04, DE-06, DE-07. AC: US-01/AC-01, US-02/AC-01.
"""

from dataclasses import dataclass

from .value_objects import PlanBlock


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
        blocks: tuple[object, ...],   # tirvi.blocks.Block tuple
        normalized: object,           # tirvi.normalize.NormalizedText
        nlp_result: object,           # tirvi.results.NLPResult
        diacritization: object,       # tirvi.results.DiacritizationResult
        g2p_result: object,           # tirvi.results.G2PResult
    ) -> "ReadingPlan":
        # TODO US-01/AC-01 (T-01): assemble PlanBlocks + PlanTokens with stable IDs
        # TODO INV-PLAN-001: assert id uniqueness
        # TODO INV-PLAN-002: preserve RTL block order
        raise NotImplementedError

    def to_json(self) -> str:
        # TODO US-01/AC-01 (T-06, INV-PLAN-003): json.dumps(asdict(self),
        #                        sort_keys=True, ensure_ascii=False, indent=2)
        raise NotImplementedError

    def to_page_json(self, ocr_result: object) -> dict[str, object]:
        # TODO US-01/AC-01 (T-07, post-review C4, INV-PLAN-004): build
        #                        {page_image_url, words[], marks_to_word_index}
        # TODO words[].bbox from ocr_result; marks_to_word_index =
        #                        {token.id: first(token.src_word_indices)}
        raise NotImplementedError
