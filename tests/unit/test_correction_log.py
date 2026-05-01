"""T-06 — CorrectionLog writer (DE-06).

AC: F48-S04/AC-01..AC-03. FT-323, FT-324, FT-330. BT-210.
INV-CCS-003.
"""

from __future__ import annotations

import json

import pytest

from tirvi.correction.log import (
    CHUNKING_PAGE_THRESHOLD,
    CORRECTIONS_SCHEMA_VERSION,
    CorrectionLog,
)
from tirvi.correction.service import PageCorrections
from tirvi.correction.value_objects import CascadeMode, CorrectionVerdict


def _make_verdict(verdict="pass", stage="nakdan_gate", original="x", corrected=None, cache_hit=False):
    return CorrectionVerdict(
        stage=stage, verdict=verdict, original=original,
        corrected_or_none=corrected, cache_hit=cache_hit,
    )


def _make_page(page_index=0, sha="sha1", verdicts=(), mode_name="full"):
    return PageCorrections(
        page_index=page_index, sha=sha,
        original_tokens=tuple("x" for _ in verdicts),
        corrected_tokens=tuple("x" for _ in verdicts),
        stage_decisions=tuple(verdicts),
        mode=CascadeMode(name=mode_name),
        applied=(), rejected=(), mode_events=(), cap_events=(),
    )


class TestCorrectionsJsonShape:
    """ADR-035 — corrections_schema_version: 1."""

    def test_writes_schema_version_1(self, tmp_path):
        log = CorrectionLog(drafts_dir=tmp_path)
        path = log.write_page(_make_page())
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["corrections_schema_version"] == CORRECTIONS_SCHEMA_VERSION

    def test_entries_carry_stage_verdict_score_candidates(self, tmp_path):
        v = _make_verdict(verdict="auto_apply", stage="mlm_scorer")
        log = CorrectionLog(drafts_dir=tmp_path)
        path = log.write_page(_make_page(verdicts=(v,)))
        entry = json.loads(path.read_text(encoding="utf-8"))["entries"][0]
        assert entry["stage"] == "mlm_scorer"
        assert entry["verdict"] == "auto_apply"
        assert "score" in entry
        assert "candidates" in entry

    def test_pass_through_excluded_by_default(self, tmp_path):
        v = _make_verdict(verdict="pass")
        log = CorrectionLog(drafts_dir=tmp_path)
        path = log.write_page(_make_page(verdicts=(v,)))
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["entries"] == []

    def test_pass_through_included_when_log_passthrough_true(self, tmp_path):
        v = _make_verdict(verdict="pass")
        log = CorrectionLog(drafts_dir=tmp_path, log_passthrough=True)
        path = log.write_page(_make_page(verdicts=(v,)))
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 1


class TestAtomicWrite:
    """AC-F48-S04/AC-02: tmp + os.replace."""

    def test_writes_via_tmp_then_replace(self, tmp_path, monkeypatch):
        import os
        replaced: list[tuple[str, str]] = []
        real_replace = os.replace

        def tracking_replace(src, dst):
            replaced.append((str(src), str(dst)))
            real_replace(src, dst)

        monkeypatch.setattr(os, "replace", tracking_replace)
        log = CorrectionLog(drafts_dir=tmp_path)
        path = log.write_page(_make_page())
        assert len(replaced) >= 1
        assert replaced[0][0].endswith(".tmp")
        assert replaced[0][1] == str(path)

    def test_partial_write_does_not_corrupt_existing_file(self, tmp_path, monkeypatch):
        import os
        log = CorrectionLog(drafts_dir=tmp_path)
        page = _make_page()
        path = log.write_page(page)
        original_content = path.read_text(encoding="utf-8")

        def boom(src, dst):
            raise OSError("disk full")

        monkeypatch.setattr(os, "replace", boom)
        log.write_page(page)
        assert path.read_text(encoding="utf-8") == original_content


class TestChunkingPolicy:
    """ADR-035: chunked corrections.<page>.json when > 50 pages."""

    def test_index_file_lists_chunks(self, tmp_path):
        log = CorrectionLog(drafts_dir=tmp_path)
        page = _make_page(page_index=CHUNKING_PAGE_THRESHOLD, sha="sha1")
        chunk_path = log.write_page(page)
        index_path = tmp_path / "sha1" / "corrections.json"
        assert index_path.exists()
        index = json.loads(index_path.read_text(encoding="utf-8"))
        assert chunk_path.name in index["chunks"]

    def test_under_threshold_uses_single_file(self, tmp_path):
        log = CorrectionLog(drafts_dir=tmp_path)
        page = _make_page(page_index=CHUNKING_PAGE_THRESHOLD - 1)
        path = log.write_page(page)
        assert path.name == "corrections.json"


class TestAuditGapPath:
    """FT-324 — disk-full / IO error path."""

    def test_oserror_writes_audit_gaps_json(self, tmp_path, monkeypatch):
        import os

        def boom(src, dst):
            raise OSError("disk full")

        monkeypatch.setattr(os, "replace", boom)
        log = CorrectionLog(drafts_dir=tmp_path)
        log.write_page(_make_page(sha="sha1"))
        gaps_path = tmp_path / "sha1" / "audit_gaps.json"
        assert gaps_path.exists()
        gaps = json.loads(gaps_path.read_text(encoding="utf-8"))
        assert len(gaps) == 1

    def test_oserror_marks_page_audit_incomplete(self, tmp_path, monkeypatch):
        import os

        def boom(src, dst):
            raise OSError("disk full")

        monkeypatch.setattr(os, "replace", boom)
        log = CorrectionLog(drafts_dir=tmp_path)
        log.write_page(_make_page(sha="sha1"))
        gaps = json.loads((tmp_path / "sha1" / "audit_gaps.json").read_text(encoding="utf-8"))
        assert gaps[0]["audit_quality"] == "audit-incomplete"

    def test_oserror_does_not_re_raise(self, tmp_path, monkeypatch):
        import os

        def boom(src, dst):
            raise OSError("disk full")

        monkeypatch.setattr(os, "replace", boom)
        log = CorrectionLog(drafts_dir=tmp_path)
        result = log.write_page(_make_page())
        assert result is not None


class TestInvariantCardinalityCheck:
    """INV-CCS-003: every applied correction has a matching log entry."""

    def test_applied_event_count_equals_log_entry_count(self, tmp_path):
        verdicts = (
            _make_verdict(verdict="auto_apply", stage="mlm_scorer"),
            _make_verdict(verdict="auto_apply", stage="mlm_scorer"),
        )
        log = CorrectionLog(drafts_dir=tmp_path)
        path = log.write_page(_make_page(verdicts=verdicts))
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["entries"]) == 2


class TestAuditTrailIntegration:
    """BT-210 — F50 inspector consumer (cross-feature)."""

    def test_log_carries_cache_hit_chain(self, tmp_path):
        v = CorrectionVerdict(
            stage="llm_reviewer", verdict="apply", original="x",
            corrected_or_none="y", cache_hit=True,
        )
        log = CorrectionLog(drafts_dir=tmp_path, log_passthrough=True)
        path = log.write_page(_make_page(verdicts=(v,)))
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["entries"][0]["cache_hit_chain"] == [True]
