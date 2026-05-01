"""HealthProbe + degraded-mode policy (DE-07).

Spec: F48 DE-07. AC: F48-S06/AC-01..AC-04.
T-07.

Init-time probe (≤ 1 s timeout):
  - Ollama  : ``GET http://127.0.0.1:11434/api/tags`` (LLMClientPort surrogate).
  - DictaBERT load (reuse F17 helper).
  - NakdanWordList load (CO13 / NakdanWordListPort).

Selects the cascade mode for the page run:
  - ``full``           : all stages healthy.
  - ``no_llm``         : Ollama unreachable; stricter MLM threshold (FT-326).
  - ``no_mlm``         : DictaBERT failed to load; deprecated
                         ``_KNOWN_OCR_FIXES`` lookup (FT-327).
  - ``emergency_fixes``: NakdanGate also unloaded; only deprecated table.
  - ``bypass``         : all stages failed; identity passthrough.

Mode is fixed per-page (INV-CCS-005).

Strict scaffold rule: NO BUSINESS LOGIC.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .value_objects import CascadeMode


@runtime_checkable
class StageHealthProbe(Protocol):
    """A single stage's health probe (DE-07)."""

    name: str

    def is_healthy(self) -> bool:  # pragma: no cover — Protocol
        ...


@dataclass(frozen=True)
class HealthCheckResult:
    """Outcome of running every probe at init.

    AC: F48-S06/AC-04.
    """

    ollama_healthy: bool
    mlm_healthy: bool
    word_list_healthy: bool
    summary: dict[str, str] = field(default_factory=dict)


@dataclass
class HealthProbe:
    """Top-level health probe + degraded-mode selector (DE-07).

    Constructor accepts the three stage probes (testable via fakes).
    ``select_mode()`` runs all probes and returns the per-page
    ``CascadeMode``.
    """

    ollama_probe: StageHealthProbe
    mlm_probe: StageHealthProbe
    word_list_probe: StageHealthProbe
    timeout_s: float = 1.0

    def run(self) -> HealthCheckResult:
        ollama = self._probe_safe(self.ollama_probe)
        mlm = self._probe_safe(self.mlm_probe)
        word_list = self._probe_safe(self.word_list_probe)
        return HealthCheckResult(ollama, mlm, word_list, self._build_summary(ollama, mlm, word_list))

    def _probe_safe(self, probe: StageHealthProbe) -> bool:
        try:
            return probe.is_healthy()
        except Exception:
            return False

    def _build_summary(self, ollama: bool, mlm: bool, word_list: bool) -> dict[str, str]:
        result: dict[str, str] = {}
        if not ollama:
            result["ollama"] = "unreachable"
        if not mlm:
            result["mlm"] = "unavailable"
        if not word_list:
            result["word_list"] = "unavailable"
        return result

    def select_mode(self, result: HealthCheckResult) -> CascadeMode:
        if self._all_down(result):
            return CascadeMode(name="bypass")
        return self._degraded_mode(result)

    def _all_down(self, result: HealthCheckResult) -> bool:
        return not result.ollama_healthy and not result.mlm_healthy and not result.word_list_healthy

    def _degraded_mode(self, result: HealthCheckResult) -> CascadeMode:
        if not result.mlm_healthy and not result.word_list_healthy:
            return CascadeMode(name="emergency_fixes")
        if not result.mlm_healthy:
            return CascadeMode(name="no_mlm")
        if not result.ollama_healthy:
            return CascadeMode(name="no_llm")
        return CascadeMode(name="full")


def _deprecated_known_fixes_lookup(token: str) -> str | None:
    """Bridge to the deprecated _KNOWN_OCR_FIXES table (FT-327).

    Used only in no_mlm / emergency_fixes modes. Named explicitly so
    removal in a later release is mechanical.
    """
    from tirvi.normalize.ocr_corrections import _KNOWN_OCR_FIXES  # noqa: PLC0415
    return _KNOWN_OCR_FIXES.get(token)


__all__ = [
    "StageHealthProbe",
    "HealthCheckResult",
    "HealthProbe",
]
