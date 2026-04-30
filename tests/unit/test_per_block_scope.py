"""F30 — per-block timing scope (no cross-block leakage).

Spec: N03/F30 DE-03. AC: US-02/AC-01.

F26 emits one TTSResult per PlanBlock (one synthesize() call per block);
voice_meta should never indicate concatenated blocks. F30 enforces the
contract by raising BlockScopeError when ``voice_meta["concatenated_blocks"]``
is truthy — defensive against future F26 evolution.
"""

import pytest

from tirvi.adapters.tts_marks.adapter import TTSEmittedTimingAdapter
from tirvi.adapters.tts_marks.invariants import BlockScopeError
from tirvi.results import TTSResult, WordMark


def _tts(*, concatenated_blocks: bool = False) -> TTSResult:
    return TTSResult(
        provider="wavenet-fake",
        audio_bytes=b"",
        codec="mp3",
        voice_meta={
            "voice": "he-IL-Wavenet-D",
            "concatenated_blocks": concatenated_blocks,
        },
        word_marks=[
            WordMark(mark_id="b1-0", start_ms=0, end_ms=100),
            WordMark(mark_id="b1-1", start_ms=500, end_ms=600),
        ],
        audio_duration_s=1.0,
    )


class TestPerBlockScope:
    def test_us_02_ac_01_single_block_voice_meta_passes(self) -> None:
        # voice_meta without concatenated_blocks (or with it False) → no raise
        out = TTSEmittedTimingAdapter(_tts()).get_timing(b"", "x y")
        assert len(out.timings) == 2

    def test_us_02_ac_01_concatenated_blocks_voice_meta_raises(self) -> None:
        with pytest.raises(BlockScopeError, match="concatenated"):
            TTSEmittedTimingAdapter(_tts(concatenated_blocks=True)).get_timing(b"", "x y")

    def test_us_02_ac_01_provider_stamp_tts_marks(self) -> None:
        out = TTSEmittedTimingAdapter(_tts()).get_timing(b"", "x y")
        assert out.provider == "tts-marks"

    def test_us_02_ac_01_source_field_tts_marks(self) -> None:
        out = TTSEmittedTimingAdapter(_tts()).get_timing(b"", "x y")
        assert out.source == "tts-marks"
