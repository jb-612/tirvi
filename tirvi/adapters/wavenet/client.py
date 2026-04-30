"""F26 — Wavenet v1beta1 client init (lazy SDK import).

Spec: N03/F26 DE-01. AC: US-01/AC-01.

The v1beta1 API is required because v1 doesn't return ``timepoints``
(SSML <mark> timing). The SDK is imported lazily inside :func:`build_client`
so module-load doesn't depend on ``google-cloud-texttospeech`` being
installed — tests can mock the SDK by patching
``sys.modules["google.cloud.texttospeech_v1beta1"]`` before calling.

Vendor-import boundary (DE-06, ADR-014): ``google.cloud.*`` is banned
project-wide by ``ruff.toml`` except under ``tirvi/adapters/**``.
"""

POC_VOICE = "he-IL-Wavenet-D"


def build_client() -> object:
    """Return a v1beta1 TextToSpeechClient.

    Lazy import — failure to import surfaces a clear, actionable error.
    """
    try:
        from google.cloud import texttospeech_v1beta1  # type: ignore[import-not-found]
    except ImportError as e:
        raise ImportError(
            "F26 requires the google-cloud-texttospeech SDK; install with "
            "`pip install google-cloud-texttospeech`"
        ) from e
    return texttospeech_v1beta1.TextToSpeechClient()
