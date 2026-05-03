# N02/F52 T-01 — BlockKind enum + taxonomy module.
#
# Spec: N02/F52 DE-01. AC: F52-S01/AC-01.
# Tests: all 8 BlockKind values importable; mixed is the documented fallback.

import pytest
from tirvi.blocks.taxonomy import (
    BlockKind,
    BLOCK_KINDS,
    FALLBACK_BLOCK_KIND,
)


_EXPECTED_KINDS = {
    "paragraph",
    "heading",
    "mixed",
    "instruction",
    "question_stem",
    "datum",
    "answer_blank",
    "multi_choice_options",
}


class TestBlockKindValues:
    def test_block_kinds_contains_all_eight_values(self):
        assert set(BLOCK_KINDS) == _EXPECTED_KINDS

    def test_block_kinds_has_exactly_eight_entries(self):
        assert len(BLOCK_KINDS) == 8

    @pytest.mark.parametrize("kind", sorted(_EXPECTED_KINDS))
    def test_each_kind_is_a_string(self, kind):
        assert isinstance(kind, str)


class TestBlockKindType:
    def test_block_kind_is_importable(self):
        # Literal types are not instances, but the annotation exists
        assert BlockKind is not None

    def test_each_kind_satisfies_block_kind_annotation(self):
        # Runtime check: every value in BLOCK_KINDS is a valid BlockKind member.
        # get_args returns the Literal members when available.
        from typing import get_args
        args = get_args(BlockKind)
        assert set(args) == _EXPECTED_KINDS


class TestFallback:
    def test_fallback_is_mixed(self):
        assert FALLBACK_BLOCK_KIND == "mixed"

    def test_fallback_is_a_member_of_block_kinds(self):
        assert FALLBACK_BLOCK_KIND in BLOCK_KINDS
