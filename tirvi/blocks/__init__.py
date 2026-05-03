"""F11 — block segmentation for OCR pages.

Heuristic-based block detection (POC scope: heading / paragraph / question_stem).
Other biz block types (table, figure, math, answer_option) are out of scope per
PLAN-POC.md and raise :class:`BlockTypeOutOfScope`.

Spec: N01/F11. Bounded context: ``bc:extraction``.
"""

from .errors import BlockTypeOutOfScope
from .taxonomy import (
    BLOCK_KINDS,
    BLOCK_TYPES,
    FALLBACK_BLOCK_KIND,
    BlockKind,
    BlockType,
)
from .value_objects import Block, PageStats

__all__ = [
    "BLOCK_KINDS",
    "BLOCK_TYPES",
    "Block",
    "BlockKind",
    "BlockType",
    "BlockTypeOutOfScope",
    "FALLBACK_BLOCK_KIND",
    "PageStats",
]
