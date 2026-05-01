"""T-07 — HealthProbe + degraded-mode policy (DE-07).

AC: F48-S06/AC-01..AC-04. FT-326, FT-327. BT-213, BT-218.
INV-CCS-005.
"""

from __future__ import annotations

import pytest

from tirvi.correction.domain.cascade import CorrectionCascade
from tirvi.correction.domain.events import CascadeModeDegraded
from tirvi.correction.errors import CascadeConfigInvalid
from tirvi.correction.health import (
    HealthCheckResult,
    HealthProbe,
    _deprecated_known_fixes_lookup,
)
from tirvi.correction.value_objects import CascadeMode


class _FakeProbe:
    def __init__(self, name: str, healthy: bool) -> None:
        self.name = name
        self._healthy = healthy

    def is_healthy(self) -> bool:
        return self._healthy


def _probe(*, ollama=True, mlm=True, word_list=True) -> HealthProbe:
    return HealthProbe(
        ollama_probe=_FakeProbe("ollama", ollama),
        mlm_probe=_FakeProbe("mlm", mlm),
        word_list_probe=_FakeProbe("wl", word_list),
    )


class TestHealthCheckProbes:
    """AC-F48-S06/AC-04: probe Ollama, DictaBERT, NakdanWordList."""

    def test_run_returns_healthcheck_result(self):
        result = _probe().run()
        assert isinstance(result, HealthCheckResult)
        assert result.ollama_healthy is True
        assert result.mlm_healthy is True
        assert result.word_list_healthy is True

    def test_unreachable_ollama_marks_unhealthy(self):
        result = _probe(ollama=False).run()
        assert result.ollama_healthy is False
        assert "ollama" in result.summary

    def test_timeout_does_not_block_init(self):
        class ExplodingProbe:
            name = "exploding"
            def is_healthy(self) -> bool:
                raise TimeoutError("simulated timeout")

        hp = HealthProbe(
            ollama_probe=ExplodingProbe(),
            mlm_probe=_FakeProbe("mlm", True),
            word_list_probe=_FakeProbe("wl", True),
        )
        result = hp.run()
        assert result.ollama_healthy is False


class TestModeSelection:
    """DE-07 decision tree."""

    def test_all_healthy_selects_full_mode(self):
        result = HealthCheckResult(True, True, True)
        mode = _probe().select_mode(result)
        assert mode.name == "full"

    def test_only_ollama_down_selects_no_llm(self):
        result = HealthCheckResult(False, True, True)
        mode = _probe().select_mode(result)
        assert mode.name == "no_llm"

    def test_mlm_down_selects_no_mlm(self):
        result = HealthCheckResult(True, False, True)
        mode = _probe().select_mode(result)
        assert mode.name == "no_mlm"

    def test_mlm_and_word_list_down_select_emergency_fixes(self):
        result = HealthCheckResult(True, False, False)
        mode = _probe().select_mode(result)
        assert mode.name == "emergency_fixes"

    def test_all_down_selects_bypass(self):
        result = HealthCheckResult(False, False, False)
        mode = _probe().select_mode(result)
        assert mode.name == "bypass"


class TestModeFixedPerPage:
    """INV-CCS-005 — BT-213: no mid-page mode flip."""

    def test_lock_mode_twice_with_different_name_raises(self):
        agg = CorrectionCascade(page_index=0, sha="s")
        agg.lock_mode(CascadeMode(name="full"))
        with pytest.raises(CascadeConfigInvalid):
            agg.lock_mode(CascadeMode(name="no_llm"))

    def test_lock_mode_twice_with_same_name_is_idempotent(self):
        agg = CorrectionCascade(page_index=0, sha="s")
        agg.lock_mode(CascadeMode(name="full"))
        agg.lock_mode(CascadeMode(name="full"))  # must not raise
        assert agg.mode.name == "full"


class TestDegradedModeBanner:
    """BT-218 — F48 emits CascadeModeDegraded; F50 owns banner copy."""

    def test_non_full_mode_emits_cascade_mode_degraded_event(self):
        agg = CorrectionCascade(page_index=0, sha="s")
        agg.lock_mode(CascadeMode(name="no_llm"))
        _, _, mode_events, _ = agg.drain_events()
        assert len(mode_events) == 1
        assert isinstance(mode_events[0], CascadeModeDegraded)
        assert mode_events[0].mode.name == "no_llm"


class TestDeprecatedKnownFixesBridge:
    """FT-327: no_mlm mode bridges to ocr_corrections._KNOWN_OCR_FIXES."""

    def test_known_fix_returns_corrected_token(self):
        assert _deprecated_known_fixes_lookup("גורס") == "גורם"

    def test_unknown_token_returns_none(self):
        assert _deprecated_known_fixes_lookup("שלום") is None
