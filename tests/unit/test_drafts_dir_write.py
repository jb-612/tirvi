"""F26 T-05 — drafts/<sha>/<block_id>.{mp3,audio.json} write.

Spec: N03/F26 DE-05. AC: US-01/AC-01.

Path format pinned by F35's consumer wire contract — block-scoped
artefacts under ``drafts/<reading-plan-sha>/``.
"""

import json
from pathlib import Path

from tirvi.adapters.wavenet.drafts import write_block_artefacts
from tirvi.results import TTSResult, WordMark


def _tts_result() -> TTSResult:
    return TTSResult(
        provider="wavenet",
        audio_bytes=b"\x00\x01\x02fake-mp3-bytes",
        codec="mp3",
        voice_meta={"voice": "he-IL-Wavenet-D", "tts_marks_truncated": False},
        word_marks=[
            WordMark(mark_id="b1-0", start_ms=0, end_ms=500),
            WordMark(mark_id="b1-1", start_ms=500, end_ms=1000),
        ],
        audio_duration_s=1.0,
    )


class TestWriteBlockArtefacts:
    def test_us_01_ac_01_writes_mp3_and_audio_json(self, tmp_path: Path) -> None:
        mp3_path, json_path = write_block_artefacts(
            tts_result=_tts_result(),
            block_id="b1",
            reading_plan_sha="abc123",
            base_dir=tmp_path,
        )
        assert mp3_path.exists()
        assert json_path.exists()

    def test_us_01_ac_01_path_uses_reading_plan_sha(self, tmp_path: Path) -> None:
        mp3_path, _ = write_block_artefacts(
            tts_result=_tts_result(),
            block_id="b1",
            reading_plan_sha="deadbeef",
            base_dir=tmp_path,
        )
        # drafts/<sha>/<block>.mp3
        assert "deadbeef" in mp3_path.parts
        assert mp3_path.name == "b1.mp3"

    def test_us_01_ac_01_path_uses_block_id(self, tmp_path: Path) -> None:
        _, json_path = write_block_artefacts(
            tts_result=_tts_result(),
            block_id="b3",
            reading_plan_sha="abc",
            base_dir=tmp_path,
        )
        assert json_path.name == "b3.audio.json"

    def test_us_01_ac_01_mp3_contains_audio_bytes(self, tmp_path: Path) -> None:
        mp3_path, _ = write_block_artefacts(
            tts_result=_tts_result(),
            block_id="b1",
            reading_plan_sha="abc",
            base_dir=tmp_path,
        )
        assert mp3_path.read_bytes() == b"\x00\x01\x02fake-mp3-bytes"

    def test_us_01_ac_01_audio_json_conforms_to_schema_keys(self, tmp_path: Path) -> None:
        _, json_path = write_block_artefacts(
            tts_result=_tts_result(),
            block_id="b1",
            reading_plan_sha="abc",
            base_dir=tmp_path,
        )
        data = json.loads(json_path.read_text(encoding="utf-8"))
        # Per docs/schemas/audio.schema.json — required keys
        assert {"block_id", "provider", "source", "timings"} <= data.keys()
        assert data["block_id"] == "b1"
        assert data["provider"] == "tts-marks"
        assert data["source"] == "tts-marks"

    def test_us_01_ac_01_audio_json_includes_audio_duration_s(self, tmp_path: Path) -> None:
        _, json_path = write_block_artefacts(
            tts_result=_tts_result(),
            block_id="b1",
            reading_plan_sha="abc",
            base_dir=tmp_path,
        )
        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["audio_duration_s"] == 1.0

    def test_us_01_ac_01_audio_json_timings_have_mark_id_and_start_s(self, tmp_path: Path) -> None:
        _, json_path = write_block_artefacts(
            tts_result=_tts_result(),
            block_id="b1",
            reading_plan_sha="abc",
            base_dir=tmp_path,
        )
        data = json.loads(json_path.read_text(encoding="utf-8"))
        timings = data["timings"]
        assert len(timings) == 2
        for t in timings:
            assert "mark_id" in t
            assert "start_s" in t

    def test_us_01_ac_01_creates_parent_dirs(self, tmp_path: Path) -> None:
        # base_dir doesn't yet contain drafts/ — the helper creates it
        _, _ = write_block_artefacts(
            tts_result=_tts_result(),
            block_id="b1",
            reading_plan_sha="newdir",
            base_dir=tmp_path,
        )
        assert (tmp_path / "drafts" / "newdir").is_dir()
