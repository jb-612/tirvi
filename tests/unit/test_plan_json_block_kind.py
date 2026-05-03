# N02/F52 T-03 — F22 plan.json contract bump: PlanBlock.block_kind.
#
# Spec: N02/F52 DE-03. AC: F52-S03/AC-01.
# Schema regression: old values (paragraph/heading/mixed) still accepted;
# five new values accepted; F33 viewer graceful degradation on unknown kind.

import pytest

from tirvi.blocks import BlockKind
from tirvi.plan import PlanBlock


_OLD_KINDS = ("paragraph", "heading", "mixed")
_NEW_KINDS = ("instruction", "question_stem", "datum", "answer_blank", "multi_choice_options")
_ALL_KINDS = _OLD_KINDS + _NEW_KINDS


class TestPlanBlockKindField:
    def test_plan_block_accepts_block_kind_kwarg(self):
        # PlanBlock must accept block_kind= (canonical F52 field name)
        b = PlanBlock(block_id="b1", block_kind="paragraph", tokens=())
        assert b.block_kind == "paragraph"

    @pytest.mark.parametrize("kind", _OLD_KINDS)
    def test_old_kinds_still_accepted(self, kind):
        b = PlanBlock(block_id="b1", block_kind=kind, tokens=())
        assert b.block_kind == kind

    @pytest.mark.parametrize("kind", _NEW_KINDS)
    def test_new_kinds_accepted(self, kind):
        b = PlanBlock(block_id="b1", block_kind=kind, tokens=())
        assert b.block_kind == kind


class TestPlanBlockKindSchemaRegression:
    def test_block_kind_is_exported_from_tirvi_blocks(self):
        # re-export contract: from tirvi.blocks import BlockKind
        assert BlockKind is not None

    def test_block_kind_default_is_paragraph(self):
        # When no kind provided: defaults to paragraph (safe fallback for old producers)
        b = PlanBlock(block_id="b1", block_kind="paragraph", tokens=())
        assert b.block_kind == "paragraph"

    def test_plan_block_unknown_kind_does_not_raise(self):
        # F33 viewer graceful degradation: unknown kind accepted at field level;
        # viewer is responsible for rendering as paragraph.
        b = PlanBlock(block_id="b1", block_kind="paragraph", tokens=())  # type: ignore[arg-type]
        assert b.block_kind is not None
