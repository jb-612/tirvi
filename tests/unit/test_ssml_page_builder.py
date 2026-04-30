"""F23 — build_page_ssml: single SSML document for the whole ReadingPlan.

Needed by the demo orchestrator which calls TTS once per page (not per block)
to get a single audio.mp3 + unified mark timeline.

Spec: N02/F23. AC: US-01/AC-01.
"""

from __future__ import annotations

from xml.etree import ElementTree as ET

import pytest

from tirvi.plan import PlanBlock, PlanToken, ReadingPlan
from tirvi.ssml.builder import build_page_ssml


def _two_block_plan() -> ReadingPlan:
    return ReadingPlan(
        page_id="page-1",
        blocks=(
            PlanBlock(
                block_id="b1",
                block_type="heading",
                tokens=(PlanToken(id="b1-0", text="שלום", src_word_indices=(0,), diacritized_text="שָׁלוֹם"),),
            ),
            PlanBlock(
                block_id="b2",
                block_type="paragraph",
                tokens=(PlanToken(id="b2-0", text="עולם", src_word_indices=(1,), diacritized_text="עוֹלָם"),),
            ),
        ),
    )


class TestBuildPageSsml:
    def test_single_speak_wrapper(self) -> None:
        ssml = build_page_ssml(_two_block_plan())
        root = ET.fromstring(ssml)
        assert root.tag == "speak"
        # xml:lang is stored under the XML namespace in ElementTree
        lang = root.get("{http://www.w3.org/XML/1998/namespace}lang") or root.get("xml:lang")
        assert lang == "he-IL"

    def test_inter_block_break_between_blocks(self) -> None:
        ssml = build_page_ssml(_two_block_plan())
        assert '<break time="500ms"/>' in ssml

    def test_first_block_has_no_leading_break(self) -> None:
        ssml = build_page_ssml(_two_block_plan())
        root = ET.fromstring(ssml)
        first_child = list(root)[0]
        assert first_child.tag == "mark", "first element should be a <mark>, not a <break>"

    def test_marks_for_all_tokens(self) -> None:
        ssml = build_page_ssml(_two_block_plan())
        root = ET.fromstring(ssml)
        marks = [m.get("name") for m in root.iter("mark")]
        assert "b1-0" in marks
        assert "b2-0" in marks

    def test_single_block_no_break(self) -> None:
        plan = ReadingPlan(
            page_id="page-1",
            blocks=(
                PlanBlock(
                    block_id="b1",
                    block_type="heading",
                    tokens=(PlanToken(id="b1-0", text="שלום", src_word_indices=(0,)),),
                ),
            ),
        )
        ssml = build_page_ssml(plan)
        assert "<break" not in ssml
