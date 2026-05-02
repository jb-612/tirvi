"""F52 T-01 — extended BlockType taxonomy + transformations field.

ADR-041 row #20 audit-trail provenance for classifier picks.
"""
from __future__ import annotations

import pytest

from tirvi.blocks.taxonomy import BLOCK_TYPES, BlockType


class TestExtendedBlockTypes:
    def test_all_eight_kinds_in_BLOCK_TYPES(self):
        expected = {
            "paragraph", "heading", "mixed",
            "instruction", "question_stem", "datum",
            "answer_blank", "multi_choice_options",
        }
        assert set(BLOCK_TYPES) == expected

    def test_legacy_three_kinds_still_first(self):
        # Producers from before F52 emit paragraph / heading / question_stem;
        # keep them at the front of the tuple so any rank-aware consumer
        # remains stable.
        assert BLOCK_TYPES[:3] == ("heading", "paragraph", "question_stem")

    @pytest.mark.parametrize("kind", [
        "instruction", "datum", "answer_blank",
        "multi_choice_options", "mixed",
    ])
    def test_new_kinds_pass_literal_assignment(self, kind: str):
        # Literal-typed assignment: should compile (mypy) and assign.
        block_kind: BlockType = kind  # type: ignore[assignment]
        assert block_kind == kind


class TestBlockTransformationsField:
    def test_block_default_transformations_is_empty_tuple(self):
        from tirvi.blocks.value_objects import Block
        b = Block(
            block_id="b1", block_type="paragraph",
            child_word_indices=(0,), bbox=(0, 0, 10, 10),
        )
        assert b.transformations == ()

    def test_block_explicit_transformations_field(self):
        from tirvi.blocks.value_objects import Block
        provenance = (
            {"kind": "block_kind_classification", "to": "instruction",
             "confidence": 0.85, "adr_row": "ADR-041 #20"},
        )
        b = Block(
            block_id="b1", block_type="instruction",
            child_word_indices=(0, 1), bbox=(0, 0, 10, 10),
            transformations=provenance,
        )
        assert b.transformations == provenance
