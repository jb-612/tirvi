"""T-05 — CorrectionCascadeService orchestrator (DE-05).

AC: F48-S01/AC-01, F48-S02/AC-03, F48-S03/AC-01.
FT-316, FT-326, FT-328, FT-329. BT-209, BT-211, BT-219.
"""

from __future__ import annotations

import pytest

from tests.unit.conftest import (
    FakeCascadeStage, FakeFeedbackReader, FakeNakdanWordList,
)
from tirvi.correction.domain.cascade import CorrectionCascade
from tirvi.correction.domain.events import CorrectionApplied, CorrectionRejected
from tirvi.correction.errors import CascadeConfigInvalid
from tirvi.correction.service import CorrectionCascadeService
from tirvi.correction.value_objects import CascadeMode, CorrectionVerdict, UserRejection


def _v(stage, verdict, original="x", corrected=None, reason=None):
    return CorrectionVerdict(
        stage=stage, verdict=verdict, original=original,
        corrected_or_none=corrected, reason=reason,
    )


PASS_V = _v("nakdan_gate", "pass")
SUSPECT_V = _v("nakdan_gate", "suspect")
AUTO_V = _v("mlm_scorer", "auto_apply", corrected="fix")
AMBIG_V = _v("mlm_scorer", "ambiguous")
APPLY_V = _v("llm_reviewer", "apply", corrected="fix")
KEEP_V = _v("llm_reviewer", "keep_original")
ANTI_V = _v("llm_reviewer", "keep_original", reason="anti_hallucination_reject")
FULL = CascadeMode(name="full")


def _svc(gate_v=PASS_V, mlm_v=KEEP_V, llm_v=KEEP_V, feedback=None, listeners=None):
    return CorrectionCascadeService(
        nakdan_gate=FakeCascadeStage(canned=gate_v),
        mlm_scorer=FakeCascadeStage(canned=mlm_v),
        llm_reviewer=FakeCascadeStage(canned=llm_v),
        feedback=feedback or FakeFeedbackReader(),
        listeners=listeners or [],
    )


class TestCascadeOrchestration:
    """AC-F48-S01/AC-01: walk gate → mlm → llm conditionally."""

    def test_pass_token_short_circuits_after_nakdan_gate(self):
        mlm = FakeCascadeStage(canned=AMBIG_V)
        llm = FakeCascadeStage(canned=APPLY_V)
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=PASS_V),
            mlm_scorer=mlm, llm_reviewer=llm,
            feedback=FakeFeedbackReader(),
        )
        svc.run_page(["x"], mode=FULL)
        assert len(mlm.calls) == 0
        assert len(llm.calls) == 0

    def test_suspect_token_advances_to_mlm_scorer(self):
        mlm = FakeCascadeStage(canned=KEEP_V)
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=SUSPECT_V),
            mlm_scorer=mlm,
            llm_reviewer=FakeCascadeStage(canned=KEEP_V),
            feedback=FakeFeedbackReader(),
        )
        svc.run_page(["x"], mode=FULL)
        assert len(mlm.calls) == 1

    def test_ambiguous_token_advances_to_llm_reviewer(self):
        llm = FakeCascadeStage(canned=KEEP_V)
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=SUSPECT_V),
            mlm_scorer=FakeCascadeStage(canned=AMBIG_V),
            llm_reviewer=llm,
            feedback=FakeFeedbackReader(),
        )
        svc.run_page(["x"], mode=FULL)
        assert len(llm.calls) == 1

    def test_auto_apply_short_circuits_after_mlm(self):
        llm = FakeCascadeStage(canned=APPLY_V)
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=SUSPECT_V),
            mlm_scorer=FakeCascadeStage(canned=AUTO_V),
            llm_reviewer=llm,
            feedback=FakeFeedbackReader(),
        )
        svc.run_page(["x"], mode=FULL)
        assert len(llm.calls) == 0


class TestPerPageAggregateLifecycle:
    """biz F48-R1-3: aggregate is transient per page."""

    def test_new_aggregate_per_page(self):
        applied_counts: list[int] = []

        class CountingListener:
            def on_correction_applied(self, e: CorrectionApplied) -> None:
                applied_counts.append(1)
            def on_correction_rejected(self, e: CorrectionRejected) -> None:
                pass
            def on_cascade_mode_degraded(self, e) -> None:
                pass
            def on_llm_call_cap_reached(self, e) -> None:
                pass

        svc = _svc(gate_v=SUSPECT_V, mlm_v=AUTO_V, listeners=[CountingListener()])
        svc.run_page(["x"], mode=FULL)
        count_after_page1 = len(applied_counts)
        svc.run_page(["x"], mode=FULL)
        assert len(applied_counts) == count_after_page1 * 2  # each page contributes independently

    def test_token_in_token_out_invariant_holds(self):
        svc = _svc(gate_v=PASS_V)
        tokens = ["א", "ב", "ג", "ד"]
        result = svc.run_page(tokens, mode=FULL)
        assert len(result.corrected_tokens) == len(tokens)


class TestUserRejectionOverride:
    """BT-211: read user rejections at init; force keep_original."""

    def test_user_rejected_token_returns_keep_original(self):
        rejection = UserRejection(
            ocr_word="bad", system_chose="fix", expected=None,
            persona_role="teacher", sentence_context_hash="h", draft_sha="sha1",
        )
        feedback = FakeFeedbackReader(rejections_by_sha={"sha1": [rejection]})
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=SUSPECT_V),
            mlm_scorer=FakeCascadeStage(canned=AUTO_V),
            llm_reviewer=FakeCascadeStage(canned=APPLY_V),
            feedback=feedback,
        )
        result = svc.run_page(["bad"], sha="sha1", mode=FULL)
        assert result.corrected_tokens[0] == "bad"  # not changed

    def test_user_rejection_emits_correction_rejected(self):
        received: list[CorrectionRejected] = []

        class RejectionListener:
            def on_correction_applied(self, e) -> None:
                pass
            def on_correction_rejected(self, e: CorrectionRejected) -> None:
                received.append(e)
            def on_cascade_mode_degraded(self, e) -> None:
                pass
            def on_llm_call_cap_reached(self, e) -> None:
                pass

        rejection = UserRejection(
            ocr_word="bad", system_chose="fix", expected=None,
            persona_role="teacher", sentence_context_hash="h", draft_sha="sha1",
        )
        feedback = FakeFeedbackReader(rejections_by_sha={"sha1": [rejection]})
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=SUSPECT_V),
            mlm_scorer=FakeCascadeStage(canned=AUTO_V),
            llm_reviewer=FakeCascadeStage(canned=APPLY_V),
            feedback=feedback,
            listeners=[RejectionListener()],
        )
        svc.run_page(["bad"], sha="sha1", mode=FULL)
        assert any(e.rejected_by == "user_override" for e in received)


class TestModeAwareDispatch:
    """FT-326/FT-327: degraded modes alter dispatch."""

    def test_no_llm_mode_skips_stage_three(self):
        llm = FakeCascadeStage(canned=APPLY_V)
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=SUSPECT_V),
            mlm_scorer=FakeCascadeStage(canned=AMBIG_V),
            llm_reviewer=llm,
            feedback=FakeFeedbackReader(),
        )
        svc.run_page(["x"], mode=CascadeMode(name="no_llm"))
        assert len(llm.calls) == 0

    def test_no_mlm_mode_skips_stage_two(self):
        mlm = FakeCascadeStage(canned=AUTO_V)
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=SUSPECT_V),
            mlm_scorer=mlm,
            llm_reviewer=FakeCascadeStage(canned=KEEP_V),
            feedback=FakeFeedbackReader(),
        )
        svc.run_page(["x"], mode=CascadeMode(name="no_mlm"))
        assert len(mlm.calls) == 0

    def test_bypass_mode_returns_identity(self):
        gate = FakeCascadeStage(canned=SUSPECT_V)
        svc = CorrectionCascadeService(
            nakdan_gate=gate,
            mlm_scorer=FakeCascadeStage(canned=AUTO_V),
            llm_reviewer=FakeCascadeStage(canned=APPLY_V),
            feedback=FakeFeedbackReader(),
        )
        result = svc.run_page(["שלום"], mode=CascadeMode(name="bypass"))
        assert result.corrected_tokens[0] == "שלום"
        assert len(gate.calls) == 0


class TestEventFanOut:
    """T-05: drain aggregate events; publish to listeners."""

    def test_listeners_receive_correction_applied(self):
        received: list[CorrectionApplied] = []

        class ApplyListener:
            def on_correction_applied(self, e: CorrectionApplied) -> None:
                received.append(e)
            def on_correction_rejected(self, e) -> None:
                pass
            def on_cascade_mode_degraded(self, e) -> None:
                pass
            def on_llm_call_cap_reached(self, e) -> None:
                pass

        svc = _svc(gate_v=SUSPECT_V, mlm_v=AUTO_V, listeners=[ApplyListener()])
        svc.run_page(["x"], mode=FULL)
        assert len(received) == 1
        assert isinstance(received[0], CorrectionApplied)

    def test_listeners_receive_correction_rejected(self):
        received: list[CorrectionRejected] = []

        class RejectListener:
            def on_correction_applied(self, e) -> None:
                pass
            def on_correction_rejected(self, e: CorrectionRejected) -> None:
                received.append(e)
            def on_cascade_mode_degraded(self, e) -> None:
                pass
            def on_llm_call_cap_reached(self, e) -> None:
                pass

        svc = _svc(gate_v=SUSPECT_V, mlm_v=AMBIG_V, llm_v=ANTI_V, listeners=[RejectListener()])
        svc.run_page(["x"], mode=FULL)
        assert len(received) == 1

    def test_listener_exception_is_swallowed_audit_resilient(self):
        class BoomListener:
            def on_correction_applied(self, e) -> None:
                raise RuntimeError("boom")
            def on_correction_rejected(self, e) -> None:
                raise RuntimeError("boom")
            def on_cascade_mode_degraded(self, e) -> None:
                pass
            def on_llm_call_cap_reached(self, e) -> None:
                pass

        svc = _svc(gate_v=SUSPECT_V, mlm_v=AUTO_V, listeners=[BoomListener()])
        result = svc.run_page(["x"], mode=FULL)
        assert result is not None  # did not raise


class TestCascadeConfigInvalid:
    """BT-219: mid-page mode flip raises CascadeConfigInvalid (INV-CCS-005)."""

    def test_mode_flip_mid_page_raises_cascade_config_invalid(self):
        agg = CorrectionCascade(page_index=0, sha="s")
        agg.lock_mode(CascadeMode(name="full"))
        with pytest.raises(CascadeConfigInvalid):
            agg.lock_mode(CascadeMode(name="no_llm"))  # different mode → conflict


class TestMLMCandidatesThreadedToLLM:
    """INV-CCS-002: LLM reviewer must receive candidates from MLM verdict."""

    def test_mlm_candidates_set_on_reviewer_before_evaluate(self):
        """When MLM returns ambiguous with candidates, service threads them
        to llm_reviewer.candidates so the prompt and anti-hallucination
        guard both see the correct options."""
        from tests.unit.conftest import FakeLLMClient, FakeNakdanWordList
        from tirvi.correction.domain.policies import AntiHallucinationPolicy
        from tirvi.correction.llm_reviewer import OllamaLLMReviewer

        word_list = FakeNakdanWordList(known={"תיקון"})
        llm_client = FakeLLMClient(
            canned_response='{"verdict":"REPLACE","chosen":"תיקון","reason":"fix"}'
        )
        reviewer = OllamaLLMReviewer(
            llm=llm_client,
            anti_hallucination=AntiHallucinationPolicy(word_list=word_list),
        )
        mlm_v = CorrectionVerdict(
            stage="mlm_scorer", verdict="ambiguous",
            original="שגויה", candidates=("תיקון",),
        )
        svc = CorrectionCascadeService(
            nakdan_gate=FakeCascadeStage(canned=SUSPECT_V),
            mlm_scorer=FakeCascadeStage(canned=mlm_v),
            llm_reviewer=reviewer,
            feedback=FakeFeedbackReader(),
        )
        result = svc.run_page(["שגויה"], mode=FULL)
        # Candidates must have been threaded: LLM was called and prompt contains the candidate
        assert len(llm_client.calls) == 1
        assert "תיקון" in llm_client.calls[0]["prompt"]
        # And the correction was applied
        assert result.corrected_tokens == ("תיקון",)
