"""T-01 — port runtime checks for the F48 correction cascade.

Spec: F48 DE-01.
AC: F48-S01/AC-01, F48-S02/AC-02, F48-S03/AC-01, F48-S04/AC-01.
"""

from __future__ import annotations

import dataclasses

import pytest

from tirvi.correction.ports import (
    FeedbackReadPort,
    ICascadeStage,
    LLMClientPort,
    NakdanWordListPort,
)
from tirvi.correction.value_objects import CorrectionVerdict, SentenceContext


class TestPortRuntimeCheckable:
    """All four F48 ports MUST be runtime_checkable Protocols (T-01)."""

    def test_icascadestage_is_runtime_checkable(self):
        class Evaluator:
            def evaluate(self, token, context):
                return None

        assert isinstance(Evaluator(), ICascadeStage)

    def test_nakdan_word_list_port_is_runtime_checkable(self):
        class FakeList:
            def is_known_word(self, token: str) -> bool:
                return False

        assert isinstance(FakeList(), NakdanWordListPort)

    def test_llm_client_port_is_runtime_checkable(self):
        class FakeClient:
            def generate(self, prompt, model_id, temperature, seed):
                return ""

        assert isinstance(FakeClient(), LLMClientPort)

    def test_feedback_read_port_is_runtime_checkable(self):
        class FakeReader:
            def user_rejections(self, draft_sha):
                return []

        assert isinstance(FakeReader(), FeedbackReadPort)


class TestCorrectionVerdictShape:
    """BO52 surface: AC-F48-S01/AC-01 / AC-F48-S04/AC-01."""

    def test_verdict_is_frozen_dataclass(self):
        v = CorrectionVerdict(stage="nakdan_gate", verdict="pass", original="שלום")
        with pytest.raises(dataclasses.FrozenInstanceError):
            v.stage = "mlm_scorer"  # type: ignore[misc]

    def test_verdict_carries_all_bo52_fields(self):
        required = {
            "stage", "verdict", "original", "corrected_or_none",
            "score", "candidates", "mode", "cache_hit", "reason",
            "model_versions", "prompt_template_version",
        }
        actual = {f.name for f in dataclasses.fields(CorrectionVerdict)}
        assert required <= actual

    def test_verdict_default_factory_for_model_versions(self):
        v1 = CorrectionVerdict(stage="nakdan_gate", verdict="pass", original="א")
        v2 = CorrectionVerdict(stage="nakdan_gate", verdict="pass", original="ב")
        assert v1.model_versions is not v2.model_versions


class TestSentenceContextShape:
    """Cache-key inputs (DE-03 / DE-04 / ADR-034)."""

    def test_sentence_context_is_frozen(self):
        ctx = SentenceContext(sentence_text="שלום", sentence_hash="abc123")
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.sentence_text = "עולם"  # type: ignore[misc]

    def test_sentence_context_has_sentence_hash(self):
        ctx = SentenceContext(sentence_text="שלום", sentence_hash="abc123")
        assert isinstance(ctx.sentence_hash, str)
