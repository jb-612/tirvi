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
        """Run all probes; return a ``HealthCheckResult`` summary.

        TODO AC-F48-S06/AC-04 (T-07): call each probe under
            ``self.timeout_s``; capture ``is_healthy`` + reason.
        TODO FT-326 (T-07): when ``not ollama_healthy`` set
            ``summary["ollama"] = "unreachable"``.
        """
        raise NotImplementedError(
            "AC-F48-S06/AC-04 / FT-326 / FT-327 — TDD T-07 fills"
        )

    def select_mode(self, result: HealthCheckResult) -> CascadeMode:
        """Map a ``HealthCheckResult`` to a ``CascadeMode`` per the
        DE-07 decision tree.

        TODO AC-F48-S06/AC-01 (T-07): all healthy → ``full``.
        TODO FT-326 (T-07): ollama only failed → ``no_llm``.
        TODO FT-327 (T-07): mlm failed → ``no_mlm`` (use deprecated
            ``_KNOWN_OCR_FIXES`` lookup).
        TODO AC-F48-S06/AC-03 (T-07): mlm + word_list failed
            → ``emergency_fixes``.
        TODO AC-F48-S06/AC-02 (T-07): all failed → ``bypass``.
        """
        raise NotImplementedError(
            "AC-F48-S06/AC-01..AC-04 / FT-326 / FT-327 — TDD T-07 fills"
        )


def _deprecated_known_fixes_lookup(token: str) -> str | None:
    """Bridge to ``tirvi/normalize/ocr_corrections.py::_KNOWN_OCR_FIXES``.

    Used only by ``no_mlm`` / ``emergency_fixes`` modes (FT-327). The
    ``_KNOWN_OCR_FIXES`` table is formally deprecated for the cascade's
    happy path — kept here behind a clearly named function so a future
    release can remove it mechanically.

    TODO T-07: import ``tirvi.normalize.ocr_corrections._KNOWN_OCR_FIXES``;
    return the corrected token or None.
    """
    raise NotImplementedError("FT-327 / AC-F48-S06/AC-03 — TDD T-07 fills")


__all__ = [
    "StageHealthProbe",
    "HealthCheckResult",
    "HealthProbe",
]
