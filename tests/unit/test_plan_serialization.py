"""F22 T-06 — deterministic JSON serialization.

Spec: N02/F22 DE-06. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-170. BT-anchors: BT-115.

``ReadingPlan.to_json()`` produces ``json.dumps(asdict(plan),
sort_keys=True, ensure_ascii=False, indent=2)``. Two runs over the
same input produce byte-identical output (basis for the
``drafts/<reading-plan-sha>/`` content-hash directory in PLAN-POC.md).
"""

import json

from tirvi.plan import PlanBlock, PlanToken, ReadingPlan


def _plan() -> ReadingPlan:
    return ReadingPlan(
        page_id="page-1",
        blocks=(
            PlanBlock(
                block_id="b1",
                block_kind="heading",
                tokens=(
                    PlanToken(
                        id="b1-0",
                        text="שלום",
                        src_word_indices=(0,),
                        pos="NOUN",
                        lemma="שלום",
                        diacritized_text="שָׁלוֹם",
                        ipa="ʃaˈlom",
                    ),
                ),
            ),
        ),
    )


class TestPlanSerialization:
    def test_us_01_ac_01_ft_170_to_json_returns_string(self) -> None:
        out = _plan().to_json()
        assert isinstance(out, str)
        assert len(out) > 0

    def test_us_02_ac_01_ft_170_to_json_byte_identical_across_runs(self) -> None:
        # Given: same plan instance
        # When:  to_json runs twice
        # Then:  outputs are byte-identical (basis for content-hash dir)
        a = _plan().to_json()
        b = _plan().to_json()
        assert a == b
        assert a.encode("utf-8") == b.encode("utf-8")

    def test_us_01_ac_01_ft_170_sort_keys_true(self) -> None:
        # Given: plan serialization
        # When:  to_json runs
        # Then:  parsed output's top-level keys appear in sorted order;
        #        every PlanBlock's keys appear sorted; every PlanToken's
        #        keys appear sorted (sort_keys=True is recursive in stdlib)
        out = _plan().to_json()
        # Cheap check — a sorted-keys serialization places "blocks" before
        # "page_id" alphabetically.
        idx_blocks = out.find('"blocks"')
        idx_page_id = out.find('"page_id"')
        assert 0 <= idx_blocks < idx_page_id

    def test_us_01_ac_01_bt_115_ensure_ascii_false_preserves_hebrew(self) -> None:
        # Given: plan with Hebrew characters
        # When:  to_json runs
        # Then:  Hebrew characters appear literally in the output (not as \uXXXX)
        out = _plan().to_json()
        assert "שלום" in out
        assert "שָׁלוֹם" in out
        assert "\\u" not in out  # no unicode escapes

    def test_us_01_ac_01_to_json_is_valid_json(self) -> None:
        # Sanity: output round-trips through json.loads
        out = _plan().to_json()
        loaded = json.loads(out)
        assert loaded["page_id"] == "page-1"
        assert len(loaded["blocks"]) == 1
        assert loaded["blocks"][0]["block_id"] == "b1"
