"""
F50 Review UI — unit tests for the Python-side /api/versions endpoint logic.

These tests exercise the _build_versions_list helper extracted from
run_demo.py's _NoCacheHandler, isolating it from the HTTP stack.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helper under test — imported via importlib so we don't add the script to
# the package path; run_demo.py is not a package module.
# ---------------------------------------------------------------------------

def _load_build_versions(tmp_path: Path):
    """Import build_versions_list from run_demo.py by exec-ing it into a namespace."""
    import importlib.util, sys
    script = Path(__file__).parent.parent.parent / "scripts" / "run_demo.py"
    spec = importlib.util.spec_from_file_location("run_demo", script)
    mod = importlib.util.module_from_spec(spec)
    # Avoid triggering main()
    sys.modules.setdefault("run_demo", mod)
    spec.loader.exec_module(mod)
    return mod.build_versions_list


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBuildVersionsList:
    def test_empty_when_drafts_missing(self, tmp_path: Path):
        fn = _load_build_versions(tmp_path)
        result = fn(tmp_path / "nonexistent")
        assert result == []

    def test_returns_list_for_each_subdir(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        (drafts / "abc123").mkdir(parents=True)
        (drafts / "def456").mkdir(parents=True)
        fn = _load_build_versions(tmp_path)
        result = fn(drafts)
        assert len(result) == 2

    def test_sha_field_present(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        (drafts / "aabbccdd").mkdir(parents=True)
        fn = _load_build_versions(tmp_path)
        result = fn(drafts)
        assert result[0]["sha"] == "aabbccdd"

    def test_mtime_field_is_number(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        (drafts / "aabbccdd").mkdir(parents=True)
        fn = _load_build_versions(tmp_path)
        result = fn(drafts)
        assert isinstance(result[0]["mtime"], (int, float))

    def test_label_field_present(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        (drafts / "aabbccdd").mkdir(parents=True)
        fn = _load_build_versions(tmp_path)
        result = fn(drafts)
        assert "label" in result[0]
        assert len(result[0]["label"]) > 0

    def test_sorted_newest_first(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        old = drafts / "oldsha"
        old.mkdir(parents=True)
        # ensure mtime differs — touch new dir after a tiny sleep
        import os
        new = drafts / "newsha"
        new.mkdir()
        # Force mtime ordering
        os.utime(old, (time.time() - 100, time.time() - 100))
        os.utime(new, (time.time(), time.time()))
        fn = _load_build_versions(tmp_path)
        result = fn(drafts)
        assert result[0]["sha"] == "newsha"
        assert result[1]["sha"] == "oldsha"

    def test_reads_metadata_from_audio_json(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        sha_dir = drafts / "abc123"
        sha_dir.mkdir(parents=True)
        audio_json = sha_dir / "audio.json"
        audio_json.write_text(json.dumps({"sha": "abc123", "timings": []}))
        fn = _load_build_versions(tmp_path)
        result = fn(drafts)
        assert result[0]["sha"] == "abc123"

    def test_graceful_when_audio_json_absent(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        (drafts / "abc123").mkdir(parents=True)
        fn = _load_build_versions(tmp_path)
        # Must not raise
        result = fn(drafts)
        assert len(result) == 1

    def test_graceful_when_audio_json_malformed(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        sha_dir = drafts / "abc123"
        sha_dir.mkdir(parents=True)
        (sha_dir / "audio.json").write_text("not json {{{{")
        fn = _load_build_versions(tmp_path)
        result = fn(drafts)
        assert len(result) == 1

    def test_skips_files_not_dirs(self, tmp_path: Path):
        drafts = tmp_path / "drafts"
        drafts.mkdir()
        (drafts / "afile.txt").write_text("x")
        (drafts / "realdir").mkdir()
        fn = _load_build_versions(tmp_path)
        result = fn(drafts)
        assert len(result) == 1
        assert result[0]["sha"] == "realdir"
