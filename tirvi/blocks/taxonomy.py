"""F11 — block-type taxonomy.

Spec: N01/F11 DE-01. AC: US-01/AC-01.
"""

from typing import Literal

# POC scope: 3 of 8 biz block types. Others raise BlockTypeOutOfScope.
BlockType = Literal["heading", "paragraph", "question_stem"]

BLOCK_TYPES: tuple[BlockType, ...] = ("heading", "paragraph", "question_stem")
