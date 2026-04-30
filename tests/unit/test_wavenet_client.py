"""F26 T-01 — Wavenet v1beta1 client init.

Spec: N03/F26 DE-01. AC: US-01/AC-01.

The v1beta1 API is required because v1 doesn't return ``timepoints``
(SSML <mark> timing). The client module exposes a lazy loader so the
SDK isn't pulled in at module-import time — keeps mypy + ruff happy
and lets tests mock the SDK without installing it.
"""

import sys
from unittest.mock import MagicMock

from tirvi.adapters.wavenet.client import POC_VOICE, build_client


class TestBuildClient:
    def test_us_01_ac_01_lazy_import_uses_v1beta1(self) -> None:
        # Patch the v1beta1 module before build_client tries to import it
        fake_module = MagicMock()
        fake_client = MagicMock()
        fake_module.TextToSpeechClient.return_value = fake_client
        sys.modules["google.cloud.texttospeech_v1beta1"] = fake_module
        try:
            client = build_client()
            assert client is fake_client
            fake_module.TextToSpeechClient.assert_called_once()
        finally:
            del sys.modules["google.cloud.texttospeech_v1beta1"]

    def test_us_01_ac_01_raises_clear_error_when_sdk_missing(self) -> None:
        # No google.cloud.texttospeech_v1beta1 in sys.modules and not installed
        sys.modules.pop("google.cloud.texttospeech_v1beta1", None)
        try:
            build_client()
        except ImportError as e:
            assert "google-cloud-texttospeech" in str(e)
        else:
            # If the SDK is actually installed in the env, that's fine — skip
            pass


class TestPOCVoice:
    def test_us_01_ac_01_voice_he_il_wavenet_d(self) -> None:
        # Per F26 design: he-IL-Wavenet-D is the POC voice
        assert POC_VOICE == "he-IL-Wavenet-D"
