"""build_manifest — enumerate run_dir stage outputs and write manifest.json.

ADR-029: stdlib only. No vendor SDK imports.
"""
import json
import os
from pathlib import Path

STAGE_LABELS: dict[str, str] = {
    "01-ocr": "OCR words",
    "02-rtl": "RTL reading order",
    "03-blocks": "Block segmentation",
    "04-normalize": "Normalized text",
    "05-nlp": "NLP tokens",
    "06-diacritize": "Diacritized text",
    "07-g2p": "Phonemes",
    "08-ssml": "SSML",
    "09-tts": "TTS audio + timing",
    "feedback": "Reviewer feedback",
}

_PIPELINE_STAGES = [k for k in STAGE_LABELS if k != "feedback"]


def _build_stage_entry(run_dir: Path, stage_name: str) -> dict:
    """Return a single stage dict for the manifest."""
    stage_dir = run_dir / stage_name
    label = STAGE_LABELS[stage_name]
    if stage_dir.is_dir():
        files = [f.name for f in stage_dir.iterdir() if f.is_file()]
        return {"name": stage_name, "label": label, "files": files, "available": True}
    return {"name": stage_name, "label": label, "files": [], "available": False}


def build_manifest(run_dir: Path) -> dict:
    """Enumerate run_dir stage dirs and write manifest.json atomically.

    Returns the manifest dict.
    """
    run_dir = Path(run_dir)
    stages = [_build_stage_entry(run_dir, name) for name in _PIPELINE_STAGES]
    manifest = {"stages": stages, "feedback_dir": "feedback/"}
    serialized = json.dumps(manifest, ensure_ascii=False, indent=2)
    tmp_path = run_dir / "manifest.json.tmp"
    tmp_path.write_text(serialized, encoding="utf-8")
    os.replace(tmp_path, run_dir / "manifest.json")
    return manifest
