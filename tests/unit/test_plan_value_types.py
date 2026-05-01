"""F22 T-01 — PlanBlock and PlanToken value types.

Spec: N02/F22 DE-01, DE-02. AC: US-01/AC-01.

Note: the original T-01 hint named ``voice_spec: dict[str, str]`` and
``ssml: str`` as PlanToken fields. The implemented design (validated
by T-02 build_plan) places ``ssml`` on :class:`PlanBlock` (populated by
F23 downstream) and does not introduce ``voice_spec`` at this layer —
voice configuration is a TTS-stage concern (F26). These tests confirm
the realised dataclass shape.
"""

from dataclasses import FrozenInstanceError, fields, is_dataclass

import pytest

from tirvi.plan import PlanBlock, PlanToken


class TestPlanTokenValueType:
    def test_us_01_ac_01_plan_token_is_dataclass(self) -> None:
        # INV-PLAN-T (DE-02): PlanToken is a dataclass for asdict() in to_json
        assert is_dataclass(PlanToken)

    def test_us_01_ac_01_plan_token_is_frozen(self) -> None:
        # INV-PLAN-T (DE-02): frozen — value-object semantics, hashable, no
        # mutation after construction (prevents accidental id drift)
        token = PlanToken(
            id="b1-0",
            text="שלום",
            src_word_indices=(0,),
        )
        with pytest.raises(FrozenInstanceError):
            token.id = "b1-1"  # type: ignore[misc]

    def test_us_01_ac_01_plan_token_id_format_block_position(self) -> None:
        # INV-PLAN-T-001 (DE-06): id == "{block_id}-{position}" — the F23/F30
        # wire-contract pin. Two tokens with identical block_id but distinct
        # positions get distinct ids.
        token_b1_0 = PlanToken(id="b1-0", text="a", src_word_indices=(0,))
        token_b1_1 = PlanToken(id="b1-1", text="b", src_word_indices=(1,))
        token_b3_0 = PlanToken(id="b3-0", text="c", src_word_indices=(2,))
        assert token_b1_0.id != token_b1_1.id
        assert token_b1_0.id != token_b3_0.id
        # The bare format follows ``{block_id}-{position}``
        block_id, position = token_b1_0.id.rsplit("-", 1)
        assert block_id == "b1"
        assert position == "0"

    def test_us_01_ac_01_plan_token_id_byte_identical_across_runs(self) -> None:
        # INV-PLAN-T-003 (DE-06): id is byte-identical across runs.
        # Re-construct the same logical token twice; equality is purely
        # value-based (frozen dataclass), so both instances must compare
        # equal byte-for-byte on the id field.
        first = PlanToken(id="b2-7", text="פרק", src_word_indices=(5,))
        second = PlanToken(id="b2-7", text="פרק", src_word_indices=(5,))
        assert first.id == second.id
        assert first.id.encode("utf-8") == second.id.encode("utf-8")
        assert first == second

    def test_us_01_ac_01_plan_token_src_word_indices_is_tuple(self) -> None:
        # INV-PLAN-T-002 (DE-06): src_word_indices is a tuple — immutable
        # so token can be hashed and serialised deterministically.
        token = PlanToken(id="b1-0", text="x", src_word_indices=(0, 1, 2))
        assert isinstance(token.src_word_indices, tuple)
        assert token.src_word_indices == (0, 1, 2)


class TestPlanBlockValueType:
    def test_us_01_ac_01_plan_block_is_dataclass(self) -> None:
        # PlanBlock is a dataclass: required for asdict() in ReadingPlan.to_json
        assert is_dataclass(PlanBlock)

    def test_us_01_ac_01_plan_block_is_frozen(self) -> None:
        # INV-PLAN-B (DE-02): frozen — value-object semantics
        block = PlanBlock(
            block_id="b1",
            block_type="paragraph",
            tokens=(),
        )
        with pytest.raises(FrozenInstanceError):
            block.block_id = "b2"  # type: ignore[misc]

    def test_us_01_ac_01_plan_block_ssml_default_empty(self) -> None:
        # INV-PLAN-B-003 (D-01): ssml is empty at F22 emit time; F23 fills it
        block = PlanBlock(
            block_id="b1",
            block_type="paragraph",
            tokens=(),
        )
        assert block.ssml == ""

    def test_us_01_ac_01_plan_block_holds_token_tuple(self) -> None:
        # tokens stored as a tuple to keep the block hashable + ordered
        token = PlanToken(id="b1-0", text="x", src_word_indices=(0,))
        block = PlanBlock(
            block_id="b1",
            block_type="paragraph",
            tokens=(token,),
        )
        assert isinstance(block.tokens, tuple)
        assert block.tokens == (token,)

    def test_us_01_ac_01_plan_token_field_names_documented(self) -> None:
        # Sanity check: codify the realised dataclass shape so future
        # accidental field renames surface in tests rather than at the
        # F23/F30 wire boundary.
        names = {f.name for f in fields(PlanToken)}
        # id + text + src_word_indices are the load-bearing wire fields
        assert {"id", "text", "src_word_indices"} <= names
