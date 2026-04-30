"""F26 — drafts/<sha>/<block_id>.{mp3,audio.json} write.

Spec: N03/F26 DE-05. AC: US-01/AC-01.

Path format pinned by F35's consumer wire contract:
``drafts/<reading-plan-sha>/<block_id>.mp3`` (audio) +
``drafts/<reading-plan-sha>/<block_id>.audio.json`` (timings).

The audio.json output conforms to ``docs/schemas/audio.schema.json``
and shares the wire format with F30's WordTimingProvider output, so
F35 consumes both paths interchangeably. F30's reconciliation
(transcript-count match) is **NOT** invoked here — F26 emits the raw
mark-projection at synthesis time; F30's reconciliation runs at
player-side when transcript context is available.
"""

import json
from pathlib import Path

from tirvi.results import TTSResult, WordMark

_PROVIDER = "tts-marks"
_LAST_MARK_FALLBACK_S = 0.2


def write_block_artefacts(
    *,
    tts_result: TTSResult,
    block_id: str,
    reading_plan_sha: str,
    base_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Write the block's mp3 + audio.json under ``drafts/<sha>/``.

    Returns ``(mp3_path, json_path)``. ``base_dir`` defaults to repo
    root (cwd); tests pass ``tmp_path``.
    """
    drafts_dir = _ensure_drafts_dir(base_dir, reading_plan_sha)
    mp3_path = drafts_dir / f"{block_id}.mp3"
    json_path = drafts_dir / f"{block_id}.audio.json"
    mp3_path.write_bytes(tts_result.audio_bytes)
    json_path.write_text(
        json.dumps(
            _audio_json_payload(tts_result, block_id),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return mp3_path, json_path


def _ensure_drafts_dir(base_dir: Path | None, reading_plan_sha: str) -> Path:
    """Create and return ``<base>/drafts/<sha>/``."""
    base = base_dir if base_dir is not None else Path.cwd()
    drafts_dir = base / "drafts" / reading_plan_sha
    drafts_dir.mkdir(parents=True, exist_ok=True)
    return drafts_dir


def _audio_json_payload(tts_result: TTSResult, block_id: str) -> dict[str, object]:
    """Build the audio.json payload from the TTSResult's marks directly."""
    marks = tts_result.word_marks or []
    return {
        "block_id": block_id,
        "provider": _PROVIDER,
        "source": _PROVIDER,
        "audio_duration_s": tts_result.audio_duration_s,
        "tts_marks_truncated": bool(
            tts_result.voice_meta.get("tts_marks_truncated", False)
        ),
        "timings": [
            _mark_to_timing_dict(marks, i, tts_result.audio_duration_s)
            for i in range(len(marks))
        ],
    }


def _mark_to_timing_dict(
    marks: list[WordMark],
    i: int,
    audio_duration_s: float | None,
) -> dict[str, object]:
    """Project a WordMark to the timing dict shape (matches F30's projection)."""
    start_s = marks[i].start_ms / 1000.0
    if i + 1 < len(marks):
        end_s: float | None = marks[i + 1].start_ms / 1000.0
    elif audio_duration_s is not None:
        end_s = audio_duration_s
    else:
        end_s = start_s + _LAST_MARK_FALLBACK_S
    return {"mark_id": marks[i].mark_id, "start_s": start_s, "end_s": end_s}
