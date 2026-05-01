"""T-05 — CorrectionCascadeService orchestrator (DE-05).

AC: F48-S01/AC-01, F48-S02/AC-03, F48-S03/AC-01.
FT-316, FT-326, FT-328, FT-329. BT-209, BT-211, BT-219.

Scaffold — TDD T-05 fills bodies.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestCascadeOrchestration:
    """AC-F48-S01/AC-01: walk gate → mlm → llm conditionally."""

    def test_pass_token_short_circuits_after_nakdan_gate(self):
        # FT-316 — happy path stops after stage 1
        pass

    def test_suspect_token_advances_to_mlm_scorer(self):
        # BT-209
        pass

    def test_ambiguous_token_advances_to_llm_reviewer(self):
        # AC-F48-S03/AC-01
        pass

    def test_auto_apply_short_circuits_after_mlm(self):
        # AC-F48-S02/AC-03
        pass


class TestPerPageAggregateLifecycle:
    """biz F48-R1-3: aggregate is transient per page."""

    def test_new_aggregate_per_page(self):
        # No state carries across pages
        pass

    def test_token_in_token_out_invariant_holds(self):
        # INV-CCS-001 — never split or merge tokens (DEP-052/053)
        pass


class TestUserRejectionOverride:
    """BT-211: read user rejections at init; force keep_original."""

    def test_user_rejected_token_returns_keep_original(self):
        pass

    def test_user_rejection_emits_correction_rejected(self):
        # rejected_by="user_override"
        pass


class TestModeAwareDispatch:
    """FT-326/FT-327: degraded modes alter dispatch."""

    def test_no_llm_mode_skips_stage_three(self):
        # FT-326
        pass

    def test_no_mlm_mode_uses_deprecated_known_fixes(self):
        # FT-327 — _KNOWN_OCR_FIXES bridge (T-07)
        pass

    def test_bypass_mode_returns_identity(self):
        pass


class TestEventFanOut:
    """T-05: drain aggregate events; publish to listeners."""

    def test_listeners_receive_correction_applied(self):
        pass

    def test_listeners_receive_correction_rejected(self):
        pass

    def test_listener_exception_is_swallowed_audit_resilient(self):
        # ADR-033 — pipeline does not abort
        pass


class TestCascadeConfigInvalid:
    """BT-219: malformed config raises CascadeConfigInvalid."""

    def test_invalid_threshold_tuple_raises_cascade_config_invalid(self):
        pass
