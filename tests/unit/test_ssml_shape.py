"""F23 T-05 — populate_plan_ssml end-to-end + assert_ssml_v1 contract.

Spec: N02/F23 DE-05, DE-06. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-178. BT-anchors: BT-118.

``populate_plan_ssml(plan)`` returns a new ReadingPlan with each
block's ``ssml`` field populated:
  - first block: just ``<speak xml:lang="he-IL">…</speak>``
  - subsequent blocks: ``<speak xml:lang="he-IL"><break time="500ms"/>…</speak>``

``assert_ssml_v1(plan)`` validates the populated plan: every block's
ssml parses, root is <speak>, mark names are unique within the plan.
"""

from xml.etree import ElementTree as ET

import pytest

from tirvi.plan import PlanBlock, PlanToken, ReadingPlan
from tirvi.ssml import populate_plan_ssml
from tirvi.ssml.contracts import SSMLContractError, assert_ssml_v1


def _two_block_plan() -> ReadingPlan:
    return ReadingPlan(
        page_id="page-1",
        blocks=(
            PlanBlock(
                block_id="b1",
                block_type="heading",
                tokens=(
                    PlanToken(
                        id="b1-0",
                        text="שלום",
                        src_word_indices=(0,),
                        diacritized_text="שָׁלוֹם",
                    ),
                ),
            ),
            PlanBlock(
                block_id="b2",
                block_type="paragraph",
                tokens=(
                    PlanToken(
                        id="b2-0",
                        text="עולם",
                        src_word_indices=(1,),
                        diacritized_text="עוֹלָם",
                    ),
                ),
            ),
        ),
    )


class TestPopulatePlanSsml:
    def test_us_01_ac_01_ft_178_returns_new_reading_plan(self) -> None:
        # Original plan unchanged (dataclasses.replace immutability)
        original = _two_block_plan()
        out = populate_plan_ssml(original)
        assert isinstance(out, ReadingPlan)
        assert out is not original
        assert original.blocks[0].ssml == ""  # original untouched

    def test_us_01_ac_01_ft_178_every_block_ssml_populated(self) -> None:
        plan = populate_plan_ssml(_two_block_plan())
        for b in plan.blocks:
            assert b.ssml != ""
            assert b.ssml.startswith('<speak xml:lang="he-IL">')
            assert b.ssml.endswith("</speak>")

    def test_us_01_ac_01_ft_178_first_block_has_no_break(self) -> None:
        plan = populate_plan_ssml(_two_block_plan())
        first = ET.fromstring(plan.blocks[0].ssml)
        # The first <speak> contains only marks, no leading <break>
        breaks = first.findall("break")
        assert len(breaks) == 0

    def test_us_02_ac_01_subsequent_blocks_lead_with_500ms_break(self) -> None:
        plan = populate_plan_ssml(_two_block_plan())
        second = ET.fromstring(plan.blocks[1].ssml)
        children = list(second)
        assert len(children) >= 1
        assert children[0].tag == "break"
        assert children[0].get("time") == "500ms"

    def test_us_01_ac_01_every_block_ssml_is_valid_xml(self) -> None:
        plan = populate_plan_ssml(_two_block_plan())
        for b in plan.blocks:
            root = ET.fromstring(b.ssml)
            assert root.tag == "speak"

    def test_us_01_ac_01_token_ids_preserved_as_mark_names(self) -> None:
        plan = populate_plan_ssml(_two_block_plan())
        all_marks: list[str] = []
        for b in plan.blocks:
            root = ET.fromstring(b.ssml)
            for m in root.findall("mark"):
                name = m.get("name")
                assert name is not None
                all_marks.append(name)
        assert all_marks == ["b1-0", "b2-0"]


class TestAssertSsmlV1:
    def test_us_01_ac_01_ft_178_valid_plan_does_not_raise(self) -> None:
        assert_ssml_v1(populate_plan_ssml(_two_block_plan()))

    def test_us_01_ac_01_bt_118_unpopulated_plan_raises(self) -> None:
        # Plan without populate_plan_ssml — block.ssml is empty
        with pytest.raises(SSMLContractError, match="empty"):
            assert_ssml_v1(_two_block_plan())

    def test_us_01_ac_01_bt_118_duplicate_mark_names_raise(self) -> None:
        # Build a plan whose tokens collide on id (impossible via from_inputs
        # but constructable directly)
        bad = ReadingPlan(
            page_id="page-1",
            blocks=(
                PlanBlock(
                    block_id="b1",
                    block_type="paragraph",
                    tokens=(
                        PlanToken(id="dup", text="a", src_word_indices=(0,)),
                        PlanToken(id="dup", text="b", src_word_indices=(1,)),
                    ),
                ),
            ),
        )
        populated = populate_plan_ssml(bad)
        with pytest.raises(SSMLContractError, match="mark"):
            assert_ssml_v1(populated)

    def test_us_01_ac_01_invalid_ssml_raises(self) -> None:
        # Manually inject malformed SSML to trigger the parse path
        plan = populate_plan_ssml(_two_block_plan())
        broken = ReadingPlan(
            page_id=plan.page_id,
            blocks=(
                PlanBlock(
                    block_id="b1",
                    block_type="paragraph",
                    tokens=plan.blocks[0].tokens,
                    ssml="<speak>not closed",
                ),
            ),
        )
        with pytest.raises(SSMLContractError):
            assert_ssml_v1(broken)
