"""CorrectionLog — auditable reasoning trail writer (DE-06).

Spec: F48 DE-06.
AC: F48-S04/AC-01, F48-S04/AC-02, F48-S04/AC-03.
ADR-035 (corrections.json schema + chunking).
T-06.
"""

from __future__ import annotations

import dataclasses
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .service import PageCorrections

CORRECTIONS_SCHEMA_VERSION: int = 1
CHUNKING_PAGE_THRESHOLD: int = 50

_PASS_THROUGH_VERDICTS = frozenset(("pass", "skip_empty", "skip_short", "skip_non_hebrew"))


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

    def write_page(self, page: PageCorrections, *, clock: object | None = None) -> Path:
        entries = self._entries_for_page(page)
        sha_dir = self.drafts_dir / page.sha
        sha_dir.mkdir(parents=True, exist_ok=True)
        is_chunked = page.page_index >= CHUNKING_PAGE_THRESHOLD
        path = self._page_path(sha_dir, page.page_index, is_chunked)
        try:
            self._atomic_write(path, self._page_doc(page, entries))
            if is_chunked:
                self._update_index(sha_dir, page, path.name)
        except OSError as exc:
            self._record_audit_gap(page.page_index, path, exc)
        return path

    def _entries_for_page(self, page: PageCorrections) -> list[CorrectionLogEntry]:
        ts = datetime.utcnow().isoformat()
        result = []
        for i, verdict in enumerate(page.stage_decisions):
            if self._should_skip(verdict):
                continue
            result.append(CorrectionLogEntry(
                page_index=page.page_index, token_index=i,
                original=verdict.original, corrected=verdict.corrected_or_none,
                stage=verdict.stage, verdict=verdict.verdict,
                score=verdict.score, candidates=verdict.candidates,
                cache_hit_chain=(verdict.cache_hit,),
                sentence_hash="",
                model_versions=dict(verdict.model_versions),
                prompt_template_version=verdict.prompt_template_version,
                ts_iso=ts, mode=page.mode.name,
            ))
        return result

    def _should_skip(self, verdict) -> bool:
        if self.log_passthrough:
            return False
        return verdict.verdict in _PASS_THROUGH_VERDICTS

    def _page_path(self, sha_dir: Path, page_index: int, is_chunked: bool) -> Path:
        if is_chunked:
            return sha_dir / f"corrections.{page_index}.json"
        return sha_dir / "corrections.json"

    def _page_doc(self, page: PageCorrections, entries: list[CorrectionLogEntry]) -> dict:
        return {
            "corrections_schema_version": self.schema_version,
            "sha": page.sha, "page_index": page.page_index,
            "mode": page.mode.name, "audit_quality": "complete",
            "entries": [dataclasses.asdict(e) for e in entries],
        }

    def _atomic_write(self, path: Path, doc: dict) -> None:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)

    def _update_index(self, sha_dir: Path, page: PageCorrections, chunk_name: str) -> None:
        index_path = sha_dir / "corrections.json"
        if index_path.exists():
            data = json.loads(index_path.read_text(encoding="utf-8"))
        else:
            data = {"corrections_schema_version": self.schema_version, "sha": page.sha, "chunks": []}
        if chunk_name not in data["chunks"]:
            data["chunks"].append(chunk_name)
        self._atomic_write(index_path, data)

    def _record_audit_gap(self, page_index: int, original_path: Path, error: Exception) -> None:
        gaps_path = original_path.parent / "audit_gaps.json"
        if gaps_path.exists():
            gaps = json.loads(gaps_path.read_text(encoding="utf-8"))
        else:
            gaps = []
        gaps.append({
            "page_index": page_index,
            "attempted_path": str(original_path),
            "error_class": type(error).__name__,
            "error_msg": str(error),
            "audit_quality": "audit-incomplete",
            "ts_iso": datetime.utcnow().isoformat(),
        })
        gaps_path.write_text(json.dumps(gaps, ensure_ascii=False, indent=2), encoding="utf-8")


__all__ = [
    "CorrectionLog",
    "CorrectionLogEntry",
    "CORRECTIONS_SCHEMA_VERSION",
    "CHUNKING_PAGE_THRESHOLD",
]
