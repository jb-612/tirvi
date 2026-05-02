"""F11 — block-segmentation value objects.

Spec: N01/F11 DE-02, DE-03, DE-04. AC: US-01/AC-01.
"""

from dataclasses import dataclass

from .taxonomy import BlockType


@dataclass(frozen=True)
class PageStats:
    """Per-page heuristic stats used by the classifier.

    Invariants (named, TDD fills):
      - INV-BLOCK-PS-001 (FT-070): median word height > 0
      - INV-BLOCK-PS-002 (FT-070): modal x-start in page frame
    """

    median_word_height: float
    modal_x_start: int
    line_spacing: float


@dataclass(frozen=True)
class Block:
    """One segmented block on a page.

    Invariants (named, TDD fills):
      - INV-BLOCK-001 (FT-071): ``block_id`` follows ``b{n}`` format (e.g., ``b3``)
      - INV-BLOCK-002 (FT-072): ``child_word_indices`` is non-empty
      - INV-BLOCK-003 (FT-072): every word index appears in exactly one block
      - INV-BLOCK-004 (DE-04): bbox is union of child word bboxes
    """

    block_id: str
    block_type: BlockType
    child_word_indices: tuple[int, ...]
    bbox: tuple[int, int, int, int]
    classifier_confidence: float | None = None
    # F52 / ADR-041: audit-trail provenance for taxonomy decisions.
    # Empty tuple for blocks whose classification is unchanged (the
    # legacy POC contract). Populated for confident non-fallback picks
    # under the F52 classifier with shape:
    #   {"kind": "block_kind_classification", "to": <BlockType>,
    #    "confidence": <float>, "adr_row": "ADR-041 #20"}
    transformations: tuple[dict, ...] = ()
