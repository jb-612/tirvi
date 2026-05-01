"""T-07 — HealthProbe + degraded-mode policy (DE-07).

AC: F48-S06/AC-01..AC-04. FT-326, FT-327. BT-213, BT-218.
INV-CCS-005.

Scaffold — TDD T-07 fills bodies.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestHealthCheckProbes:
    """AC-F48-S06/AC-04: probe Ollama, DictaBERT, NakdanWordList."""

    def test_run_returns_healthcheck_result(self):
        pass

    def test_unreachable_ollama_marks_unhealthy(self):
        pass

    def test_timeout_does_not_block_init(self):
        # ≤ 1 s timeout
        pass


class TestModeSelection:
    """DE-07 decision tree."""

    def test_all_healthy_selects_full_mode(self):
        # AC-F48-S06/AC-01
        pass

    def test_only_ollama_down_selects_no_llm(self):
        # FT-326
        pass

    def test_mlm_down_selects_no_mlm(self):
        # FT-327 — uses _KNOWN_OCR_FIXES bridge
        pass

    def test_mlm_and_word_list_down_select_emergency_fixes(self):
        # AC-F48-S06/AC-03
        pass

    def test_all_down_selects_bypass(self):
        # AC-F48-S06/AC-02
        pass


class TestModeFixedPerPage:
    """INV-CCS-005 — BT-213: no mid-page mode flip."""

    def test_lock_mode_twice_with_different_name_raises(self):
        pass

    def test_lock_mode_twice_with_same_name_is_idempotent(self):
        pass


class TestDegradedModeBanner:
    """BT-218 — F48 emits CascadeModeDegraded; F50 owns banner copy."""

    def test_non_full_mode_emits_cascade_mode_degraded_event(self):
        pass


class TestDeprecatedKnownFixesBridge:
    """FT-327: no_mlm mode bridges to ocr_corrections._KNOWN_OCR_FIXES."""

    def test_known_fix_returns_corrected_token(self):
        pass

    def test_unknown_token_returns_none(self):
        pass
