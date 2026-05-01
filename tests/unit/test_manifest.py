"""Unit tests for tirvi.debug.manifest.build_manifest.

T-03: N04/F33 — Exam Review Portal
AC: US-05/AC-22, US-05/AC-24
FT: FT-319, FT-320
"""
import json
from pathlib import Path

import pytest

from tirvi.debug.manifest import STAGE_LABELS, build_manifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stage(manifest: dict, name: str) -> dict:
    """Return the stage entry with the given name from the manifest dict."""
    for stage in manifest["stages"]:
        if stage["name"] == name:
            return stage
    raise KeyError(f"Stage {name!r} not found in manifest")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_manifest_written_to_run_dir(tmp_path: Path) -> None:
    """manifest.json is written to run_dir after build_manifest call."""
    build_manifest(tmp_path)
    assert (tmp_path / "manifest.json").exists()


def test_manifest_has_stages_key(tmp_path: Path) -> None:
    """Returned dict contains a 'stages' key with a list."""
    result = build_manifest(tmp_path)
    assert "stages" in result
    assert isinstance(result["stages"], list)


def test_manifest_has_feedback_dir(tmp_path: Path) -> None:
    """Returned dict has feedback_dir == 'feedback/'."""
    result = build_manifest(tmp_path)
    assert result["feedback_dir"] == "feedback/"


def test_present_stage_is_available(tmp_path: Path) -> None:
    """A stage whose directory exists is marked available: True."""
    ocr_dir = tmp_path / "01-ocr"
    ocr_dir.mkdir()
    (ocr_dir / "data.json").write_text("{}", encoding="utf-8")

    result = build_manifest(tmp_path)
    stage = _stage(result, "01-ocr")
    assert stage["available"] is True


def test_present_stage_lists_files(tmp_path: Path) -> None:
    """A present stage includes its file names (relative, no subdirs)."""
    ocr_dir = tmp_path / "01-ocr"
    ocr_dir.mkdir()
    (ocr_dir / "data.json").write_text("{}", encoding="utf-8")

    result = build_manifest(tmp_path)
    stage = _stage(result, "01-ocr")
    assert "data.json" in stage["files"]


def test_missing_stage_is_unavailable(tmp_path: Path) -> None:
    """A stage whose directory is absent is marked available: False."""
    result = build_manifest(tmp_path)
    stage = _stage(result, "04-normalize")
    assert stage["available"] is False


def test_missing_stage_has_empty_files(tmp_path: Path) -> None:
    """A stage whose directory is absent has files: []."""
    result = build_manifest(tmp_path)
    stage = _stage(result, "04-normalize")
    assert stage["files"] == []


def test_stage_label_is_human_readable(tmp_path: Path) -> None:
    """The 01-ocr stage carries the label 'OCR words'."""
    result = build_manifest(tmp_path)
    stage = _stage(result, "01-ocr")
    assert stage["label"] == "OCR words"


def test_all_known_stages_present_in_output(tmp_path: Path) -> None:
    """All 9 pipeline stages (excluding 'feedback') appear in the manifest."""
    result = build_manifest(tmp_path)
    expected = [k for k in STAGE_LABELS if k != "feedback"]
    names_in_manifest = [s["name"] for s in result["stages"]]
    assert sorted(names_in_manifest) == sorted(expected)


def test_manifest_json_is_valid(tmp_path: Path) -> None:
    """The written manifest.json parses as valid JSON."""
    build_manifest(tmp_path)
    text = (tmp_path / "manifest.json").read_text(encoding="utf-8")
    parsed = json.loads(text)
    assert "stages" in parsed


def test_write_is_atomic(tmp_path: Path) -> None:
    """No .tmp file is left behind after build_manifest returns."""
    build_manifest(tmp_path)
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert tmp_files == []


def test_idempotent(tmp_path: Path) -> None:
    """Calling build_manifest twice produces the same result without error."""
    first = build_manifest(tmp_path)
    second = build_manifest(tmp_path)
    assert first == second
    assert (tmp_path / "manifest.json").exists()
