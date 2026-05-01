"""CorrectionLog — auditable reasoning trail writer (DE-06).

Spec: F48 DE-06.
AC: F48-S04/AC-01, F48-S04/AC-02, F48-S04/AC-03.
ADR-035 (corrections.json schema + chunking).
T-06.

Writes ``drafts/<sha>/corrections.json`` (single JSON array per page) with
``corrections_schema_version: 1``. When document > 50 pages, chunked as
``corrections.<page>.json`` with an index file (ADR-035).

On disk-full / IO error, appends to ``drafts/<sha>/audit_gaps.json`` and
marks the page header ``audit_quality: "audit-incomplete"`` — pipeline
does NOT abort (FT-324).

Strict scaffold rule: NO BUSINESS LOGIC. ``write_page`` body raises
``NotImplementedError`` — TDD T-06 fills.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .service import PageCorrections

CORRECTIONS_SCHEMA_VERSION: int = 1
CHUNKING_PAGE_THRESHOLD: int = 50


@dataclass(frozen=True)
class CorrectionLogEntry:
    """One row in ``corrections.json`` (BO55).

    AC: F48-S04/AC-01, F48-S04/AC-02.
    Spec: F48 DE-06.
    """

    page_index: int
    token_index: int
    original: str
    corrected: str | None
    stage: str                                # nakdan_gate | mlm_scorer | llm_reviewer | deprecated_table
    verdict: str
    score: float | None
    candidates: tuple[str, ...]
    cache_hit_chain: tuple[bool, ...]         # one bool per stage walked
    sentence_hash: str
    model_versions: dict[str, str] = field(default_factory=dict)
    prompt_template_version: str | None = None
    ts_iso: str = ""
    mode: str = "full"


@dataclass
class CorrectionLog:
    """Writer for ``corrections.json`` and ``audit_gaps.json`` (DE-06).

    Constructor takes the drafts dir root; ``write_page`` writes a single
    page's log atomically (`.tmp` then ``os.replace``).

    Pass-through entries (``stage="nakdan_gate", verdict="pass"``) are
    NOT logged unless ``log_passthrough=True`` (FT-323).
    """

    drafts_dir: Path
    log_passthrough: bool = False
    schema_version: int = CORRECTIONS_SCHEMA_VERSION

    # ---- entry point ------------------------------------------------------

    def write_page(
        self,
        page: PageCorrections,
        *,
        clock: object | None = None,
    ) -> Path:
        """Write the page's correction log to disk; return the file path.

        TODO INV-CCS-003 (T-06): assert every applied event has a
            matching ``CorrectionLogEntry``; raise
            ``CascadeInvariantViolation`` on cardinality mismatch.
        TODO AC-F48-S04/AC-01 (T-06): build entries from
            ``page.stage_decisions``; skip pass-through unless
            ``self.log_passthrough``.
        TODO AC-F48-S04/AC-02 (T-06): atomic write — write
            ``corrections.<page>.json.tmp`` then ``os.replace``.
        TODO AC-F48-S04/AC-03 (ADR-035): if the doc exceeds
            ``CHUNKING_PAGE_THRESHOLD`` pages, also update the index
            ``corrections.json`` `chunks` array.
        TODO FT-324 (T-06): on ``OSError`` from ``os.replace``, append
            to ``audit_gaps.json`` and stamp the page
            ``audit_quality: "audit-incomplete"``; do NOT re-raise.
        """
        raise NotImplementedError(
            "AC-F48-S04/AC-01..AC-03 / FT-323 / FT-324 / INV-CCS-003 — "
            "TDD T-06 fills"
        )

    # ---- helpers (named, NotImplemented) ----------------------------------

    def _entries_for_page(
        self, page: PageCorrections
    ) -> Sequence[CorrectionLogEntry]:
        """Project ``PageCorrections`` into log entries.

        TODO T-06: filter pass-through if ``not self.log_passthrough``;
            map each ``CorrectionVerdict`` → ``CorrectionLogEntry``;
            stamp ``ts_iso`` from injected clock (deterministic tests).
        """
        raise NotImplementedError("AC-F48-S04/AC-01 — TDD T-06 fills")

    def _record_audit_gap(
        self, page_index: int, original_path: Path, error: Exception
    ) -> None:
        """Record a disk-full / IO error to ``audit_gaps.json``.

        TODO FT-324 (T-06): append a row
            ``{page_index, attempted_path, error_class, error_msg, ts_iso}``
            to ``audit_gaps.json``; create the file with `[]` if missing.
        """
        raise NotImplementedError("FT-324 — TDD T-06 fills")


__all__ = [
    "CorrectionLog",
    "CorrectionLogEntry",
    "CORRECTIONS_SCHEMA_VERSION",
    "CHUNKING_PAGE_THRESHOLD",
]
