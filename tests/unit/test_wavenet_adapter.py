"""F26 T-06 — WavenetTTSAdapter contract conformance.

Spec: N03/F26 DE-06. AC: US-01/AC-01.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from tirvi.adapters.wavenet.adapter import WavenetTTSAdapter
from tirvi.ports import TTSBackend
from tirvi.results import TTSResult


def _mock_response() -> MagicMock:
    r = MagicMock()
    r.audio_content = b"<mp3>"
    r.timepoints = [MagicMock(mark_name="b1-0", time_seconds=0.0)]
    r.audio_duration = None
    return r


class TestWavenetTTSAdapter:
    def test_us_01_ac_01_implements_tts_backend(self) -> None:
        adapter = WavenetTTSAdapter()
        # @runtime_checkable Protocol from F03
        assert isinstance(adapter, TTSBackend)

    def test_us_01_ac_01_returns_tts_result(self) -> None:
        adapter = WavenetTTSAdapter()
        client = MagicMock()
        client.synthesize_speech = MagicMock(return_value=_mock_response())
        with patch(
            "tirvi.adapters.wavenet.adapter.build_client", return_value=client
        ):
            result = adapter.synthesize("<speak/>", "he-IL-Wavenet-D")
        assert isinstance(result, TTSResult)

    def test_us_01_ac_01_default_voice_is_he_il_wavenet_d(self) -> None:
        # When the operator passes the empty voice, adapter falls back to POC
        adapter = WavenetTTSAdapter()
        client = MagicMock()
        client.synthesize_speech = MagicMock(return_value=_mock_response())
        with patch(
            "tirvi.adapters.wavenet.adapter.build_client", return_value=client
        ):
            result = adapter.synthesize("<speak/>", "")
        assert result.voice_meta["voice"] == "he-IL-Wavenet-D"

    @pytest.mark.skipif(
        bool(os.environ.get("TIRVI_F26_SKIP_LIVE", "1")),
        reason="F26 live API test skipped (set TIRVI_F26_SKIP_LIVE=0 + GCP creds to enable)",
    )
    def test_us_01_ac_01_live_synthesize_returns_audio_with_marks(self) -> None:
        # Real call — verifies the adapter against actual Wavenet.
        # ~$0.0001 per run on this short utterance.
        ssml = '<speak xml:lang="he-IL"><mark name="t-0"/>שלום</speak>'
        adapter = WavenetTTSAdapter()
        result = adapter.synthesize(ssml, "he-IL-Wavenet-D")
        assert isinstance(result, TTSResult)
        assert len(result.audio_bytes) > 1000   # real mp3 is non-trivial
        assert result.word_marks is not None
        assert len(result.word_marks) == 1
        assert result.word_marks[0].mark_id == "t-0"
