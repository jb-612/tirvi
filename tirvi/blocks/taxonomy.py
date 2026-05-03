"""F11 + F52 — block-type taxonomy.

Spec: N01/F11 DE-01, N02/F52 DE-01. AC: F52-S01/AC-01.

Originally three POC values (heading / paragraph / question_stem)
per F11. F52 extends the taxonomy with five more kinds for reading-
disability accommodations (per roadmap PR #30, ADR-041 row #20):

  - ``mixed`` — fallback when classifier confidence is below threshold;
    chosen over ``unknown`` per PR #30 reviewer Q2 answer.
  - ``instruction`` — set-up text the student must understand (e.g.,
    leading paragraph that begins with `הוראות`, `קרא בעיון`).
  - ``datum`` — supporting text/table cell/image alt that the question
    operates on.
  - ``answer_blank`` — empty area the student fills in (visual blank
    line, underline-only line).
  - ``multi_choice_options`` — closed-option list `א./ב./ג./ד.` for
    multiple-choice questions.

The first three (heading / paragraph / question_stem) keep their
positions at the front of ``BLOCK_TYPES`` so any rank-aware consumer
that pre-dates F52 stays stable.
"""

from typing import Literal

BlockType = Literal[
    "heading",
    "paragraph",
    "question_stem",
    "mixed",
    "instruction",
    "datum",
    "answer_blank",
    "multi_choice_options",
]

# F52 DE-01 — canonical public name; BlockType kept for back-compat.
BlockKind = BlockType

BLOCK_TYPES: tuple[BlockType, ...] = (
    "heading",
    "paragraph",
    "question_stem",
    "mixed",
    "instruction",
    "datum",
    "answer_blank",
    "multi_choice_options",
)

# F52 DE-01 — canonical public name; BLOCK_TYPES kept for back-compat.
BLOCK_KINDS: tuple[BlockKind, ...] = BLOCK_TYPES

# Classifier emits this when confidence falls below threshold (ADR-041 #20).
FALLBACK_BLOCK_KIND: BlockKind = "mixed"
