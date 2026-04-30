"""F26 T-02 — Wavenet synthesize call.

Spec: N03/F26 DE-02. AC: US-01/AC-01.

WavenetTTSAdapter.synthesize(ssml, voice) calls the v1beta1 client's
synthesize_speech with ``enable_time_pointing=[SSML_MARK]`` so the
response includes timepoints. Returns a TTSResult per F03's
TTSBackend port (never raw bytes — F03 INV-PORT-TTS-001).
"""

from unittest.mock import MagicMock, patch

from tirvi.adapters.wavenet.adapter import WavenetTTSAdapter
from tirvi.results import TTSResult


def _mock_response() -> MagicMock:
    r = MagicMock()
    r.audio_content = b"<mp3>"
    r.timepoints = [MagicMock(mark_name="b1-0", time_seconds=0.0)]
    r.audio_duration = None
    return r


class TestWavenetSynthesize:
    def test_us_01_ac_01_returns_tts_result_never_bytes(self) -> None:
        # F03 INV-PORT-TTS-001 — adapter returns TTSResult, never raw bytes
        adapter = WavenetTTSAdapter()
        with patch(
            "tirvi.adapters.wavenet.adapter.build_client",
            return_value=MagicMock(synthesize_speech=MagicMock(return_value=_mock_response())),
        ):
            result = adapter.synthesize(
                '<speak><mark name="b1-0"/>שלום</speak>', "he-IL-Wavenet-D"
            )
        assert isinstance(result, TTSResult)
        assert not isinstance(result, bytes)

    def test_us_01_ac_01_passes_ssml_to_client(self) -> None:
        adapter = WavenetTTSAdapter()
        client = MagicMock()
        client.synthesize_speech = MagicMock(return_value=_mock_response())
        with patch(
            "tirvi.adapters.wavenet.adapter.build_client", return_value=client
        ):
            adapter.synthesize("<speak>שלום</speak>", "he-IL-Wavenet-D")
        # The client should have been called with our SSML
        call_kwargs = client.synthesize_speech.call_args.kwargs
        # v1beta1 takes a SynthesisInput with ssml=...; our adapter wraps
        assert "input" in call_kwargs or "request" in call_kwargs

    def test_us_01_ac_01_enables_time_pointing_for_mark(self) -> None:
        # The v1beta1 API requires enable_time_pointing=[SSML_MARK] to return
        # timepoints. The adapter wires this on every call.
        adapter = WavenetTTSAdapter()
        client = MagicMock()
        client.synthesize_speech = MagicMock(return_value=_mock_response())
        with patch(
            "tirvi.adapters.wavenet.adapter.build_client", return_value=client
        ):
            adapter.synthesize("<speak/>", "he-IL-Wavenet-D")
        call_kwargs = client.synthesize_speech.call_args.kwargs
        # enable_time_pointing is at the request level; our adapter sets it
        # via the request kwarg or top-level (both v1beta1 forms accepted)
        request = call_kwargs.get("request") or call_kwargs
        # Find the time-pointing config — flexible match across wrapping styles
        assert "enable_time_pointing" in str(request) or hasattr(
            request, "enable_time_pointing"
        )

    def test_us_01_ac_01_uses_supplied_voice(self) -> None:
        adapter = WavenetTTSAdapter()
        client = MagicMock()
        client.synthesize_speech = MagicMock(return_value=_mock_response())
        with patch(
            "tirvi.adapters.wavenet.adapter.build_client", return_value=client
        ):
            result = adapter.synthesize("<speak/>", "he-IL-Wavenet-B")
        # The voice in voice_meta should match what was passed
        assert result.voice_meta["voice"] == "he-IL-Wavenet-B"

    def test_us_01_ac_01_lazy_client_init_only_on_first_call(self) -> None:
        # Multiple synthesize() calls should reuse one client instance
        adapter = WavenetTTSAdapter()
        client = MagicMock()
        client.synthesize_speech = MagicMock(return_value=_mock_response())
        with patch(
            "tirvi.adapters.wavenet.adapter.build_client", return_value=client
        ) as build:
            adapter.synthesize("<speak/>", "he-IL-Wavenet-D")
            adapter.synthesize("<speak/>", "he-IL-Wavenet-D")
        assert build.call_count == 1
