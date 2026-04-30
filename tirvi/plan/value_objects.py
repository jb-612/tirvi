"""F22 — reading-plan value objects.

Spec: N02/F22 DE-02. AC: US-01/AC-01.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanToken:
    """One token in the reading plan with stable ID for cross-stage reference.

    Invariants (named, TDD fills):
      - INV-PLAN-T-001 (DE-06): ``id == f"{block_id}-{position}"`` (e.g., ``b3-0``)
      - INV-PLAN-T-002 (DE-06): ``src_word_indices`` non-empty
      - INV-PLAN-T-003 (DE-06): id is byte-identical across runs (basis for content hash)
      - INV-PLAN-T-004 (F23 wire): ``id`` matches SSML ``<mark name="…"/>`` pin
      - INV-PLAN-T-005 (F30 wire): ``id`` matches WordTimingResult.timings[].mark_id
    """

    id: str
    text: str
    src_word_indices: tuple[int, ...]
    pos: str | None = None
    lemma: str | None = None
    diacritized_text: str | None = None
    ipa: str | None = None
    stress: int | None = None


@dataclass(frozen=True)
class PlanBlock:
    """One block in the reading plan.

    Invariants (named, TDD fills):
      - INV-PLAN-B-001 (DE-02): ``block_id`` matches F11 :class:`tirvi.blocks.Block`
      - INV-PLAN-B-002 (DE-05): blocks with empty ``tokens`` are filtered upstream
      - INV-PLAN-B-003 (D-01): ``ssml`` populated by F23, empty at F22 emit time
    """

    block_id: str
    block_type: str
    tokens: tuple[PlanToken, ...]
    ssml: str = ""
    bbox: tuple[int, int, int, int] | None = None
