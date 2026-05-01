"""AuditSink — writes pipeline stage outputs to disk for debug review.

ADR-029: stdlib + domain dict types only. No vendor SDK imports.
"""
import copy
import json
import os
from pathlib import Path


class AuditSink:
    """Serializes pipeline stage payloads to <run_dir>/<stage>/data.json."""

    def __init__(self, out_dir: Path) -> None:
        self._out_dir = Path(out_dir)
        self._manifest: dict = {}

    def write(self, stage_name: str, payload: dict, run_dir: Path) -> None:
        """Write payload as JSON to run_dir/<stage_name>/data.json (atomic)."""
        stage_dir = Path(run_dir) / stage_name
        stage_dir.mkdir(parents=True, exist_ok=True)
        data_file = stage_dir / "data.json"
        tmp_file = stage_dir / "data.json.tmp"
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        tmp_file.write_text(serialized, encoding="utf-8")
        os.replace(tmp_file, data_file)
        self._manifest[stage_name] = {"files": ["data.json"], "available": True}

    def write_ocr(self, payload: dict, run_dir: Path) -> None:
        self.write("01-ocr", payload, run_dir)

    def write_normalized(self, payload: dict, run_dir: Path) -> None:
        self.write("04-normalize", payload, run_dir)

    def write_nlp(self, payload: dict, run_dir: Path) -> None:
        self.write("05-nlp", payload, run_dir)

    def write_diacritized(self, payload: dict, run_dir: Path) -> None:
        self.write("06-diacritize", payload, run_dir)

    def write_ssml(self, payload: dict, run_dir: Path) -> None:
        self.write("08-ssml", payload, run_dir)

    def write_tts(self, payload: dict, run_dir: Path) -> None:
        self.write("09-tts", payload, run_dir)

    @property
    def manifest(self) -> dict:
        """Return a deep copy of the internal manifest."""
        return copy.deepcopy(self._manifest)
