"""Unit tests for AuditSink — RED phase.

All tests must fail before tirvi/debug/sink.py is created.
"""
import json
from pathlib import Path

import pytest

from tirvi.debug.sink import AuditSink


def test_write_creates_stage_directory(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write("01-ocr", {"words": ["hello"]}, run_dir)
    assert (run_dir / "01-ocr").is_dir()


def test_write_serializes_payload_as_json(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    payload = {"words": ["שלום"], "count": 3}
    sink.write("01-ocr", payload, run_dir)
    data_file = run_dir / "01-ocr" / "data.json"
    assert data_file.exists()
    loaded = json.loads(data_file.read_text(encoding="utf-8"))
    assert loaded == payload


def test_write_updates_manifest(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write("01-ocr", {}, run_dir)
    assert sink.manifest["01-ocr"]["available"] is True


def test_write_ocr_uses_correct_stage_name(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write_ocr({}, run_dir)
    assert (run_dir / "01-ocr").is_dir()


def test_write_normalized_uses_correct_stage_name(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write_normalized({}, run_dir)
    assert (run_dir / "04-normalize").is_dir()


def test_write_nlp_uses_correct_stage_name(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write_nlp({}, run_dir)
    assert (run_dir / "05-nlp").is_dir()


def test_write_diacritized_uses_correct_stage_name(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write_diacritized({}, run_dir)
    assert (run_dir / "06-diacritize").is_dir()


def test_write_ssml_uses_correct_stage_name(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write_ssml({}, run_dir)
    assert (run_dir / "08-ssml").is_dir()


def test_write_tts_uses_correct_stage_name(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write_tts({}, run_dir)
    assert (run_dir / "09-tts").is_dir()


def test_manifest_property_returns_copy(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write("01-ocr", {}, run_dir)
    m1 = sink.manifest
    m1["01-ocr"]["available"] = False
    m2 = sink.manifest
    assert m2["01-ocr"]["available"] is True


def test_multiple_writes_accumulate_in_manifest(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write("01-ocr", {}, run_dir)
    sink.write("05-nlp", {"tokens": []}, run_dir)
    manifest = sink.manifest
    assert "01-ocr" in manifest
    assert "05-nlp" in manifest
    assert manifest["01-ocr"]["available"] is True
    assert manifest["05-nlp"]["available"] is True


def test_write_is_atomic(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    sink.write("01-ocr", {"x": 1}, run_dir)
    data_file = run_dir / "01-ocr" / "data.json"
    tmp_file = run_dir / "01-ocr" / "data.json.tmp"
    assert data_file.exists()
    assert not tmp_file.exists()
    loaded = json.loads(data_file.read_text(encoding="utf-8"))
    assert loaded == {"x": 1}


def test_payload_must_be_json_serializable(tmp_path):
    sink = AuditSink(out_dir=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()
    with pytest.raises(TypeError):
        sink.write("01-ocr", {"fn": lambda: None}, run_dir)
