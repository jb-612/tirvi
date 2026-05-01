"""In-memory fake registry for every port (F03 DE-04).

Fakes are **fixture-driven** (JSON/dict per port under ``tests/fixtures/``),
**deterministic** across N invocations, and cover the happy path + at least one
documented failure mode per port.

This module ships **shells only** (every method ``raise NotImplementedError``).
The shared fake registry — fixture loading + canned-result wiring — is filled
by ``@test-mock-registry`` after F03's Gate 4 lands. See plan §H.
"""

from .errors import AdapterError
from .ports import (
    DiacritizerBackend,
    G2PBackend,
    NLPBackend,
    OCRBackend,
    TTSBackend,
    WordTimingProvider,
)
from .results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
    OCRResult,
    TTSResult,
    WordTimingResult,
)


class OCRBackendFake(OCRBackend):
    """Deterministic in-memory OCR fake.

    Spec: F03 DE-04. AC: US-01/AC-01. FT-anchor: FT-015. BT-anchor: BT-010.
    """

    def __init__(self, fixture_path: str | None = None) -> None:
        # TODO US-01/AC-01: load fixture (happy path + 1 failure mode); deterministic
        self._fixture_path = fixture_path

    def ocr_pdf(self, pdf_bytes: bytes) -> OCRResult:
        # TODO FT-015: return canned OCRResult; identical across N calls
        # TODO BT-010: documented failure-mode fixture raises typed AdapterError
        raise NotImplementedError


class NLPBackendFake(NLPBackend):
    """Deterministic in-memory NLP fake.

    Spec: F03 DE-04. AC: US-01/AC-01. BT-anchor: BT-010, BT-011.
    """

    def __init__(self, fixture_path: str | None = None) -> None:
        # TODO US-01/AC-01: load Hebrew UD tokenization fixture
        self._fixture_path = fixture_path

    def analyze(self, text: str, lang: str) -> NLPResult:
        raise NotImplementedError


class DiacritizerBackendFake(DiacritizerBackend):
    """Deterministic in-memory diacritization fake.

    Spec: F03 DE-04. AC: US-01/AC-01. BT-anchor: BT-010.
    """

    def __init__(self, fixture_path: str | None = None) -> None:
        # TODO US-01/AC-01: load nikud-insertion fixture (NFC→NFD per F19)
        self._fixture_path = fixture_path

    def diacritize(self, text: str) -> DiacritizationResult:
        raise NotImplementedError


class G2PBackendFake(G2PBackend):
    """Deterministic in-memory G2P fake.

    Per ADR-028 (F20 T-08), the fake emits whole-text IPA as a single
    ``["fake-ipa"]`` element — mirroring the production Phonikud
    adapter's whole-text shape rather than per-token entries.

    Spec: F03 DE-04. AC: US-01/AC-01. BT-anchor: BT-010.
    """

    def __init__(self, fixture_path: str | None = None) -> None:
        self._fixture_path = fixture_path

    def grapheme_to_phoneme(self, text: str, lang: str) -> G2PResult:
        return G2PResult(provider="g2p-fake", phonemes=["fake-ipa"], confidence=None)


class TTSBackendFake(TTSBackend):
    """Deterministic in-memory TTS fake.

    Two fixture variants per design:
      - ``marks-present`` (Wavenet-like — FT-012)
      - ``marks-absent`` (Chirp-3-HD-like — FT-013)

    Spec: F03 DE-04. AC: US-01/AC-01. FT-anchor: FT-012, FT-013. BT-anchor: BT-010.
    """

    def __init__(self, fixture_path: str | None = None) -> None:
        # TODO US-01/AC-01: load fixture; supports both marks-present and marks-absent
        self._fixture_path = fixture_path

    def synthesize(self, ssml: str, voice: str) -> TTSResult:
        # TODO FT-012: marks-present fixture returns TTSResult.word_marks populated
        # TODO FT-013: marks-absent fixture returns TTSResult.word_marks is None
        raise NotImplementedError


class WordTimingProviderFake(WordTimingProvider):
    """Deterministic in-memory WordTimingProvider fake.

    Routes per ``WordTimingResult.source`` field:
      - ``"tts-marks"`` (happy path)
      - ``"forced-alignment"`` (fallback path — BT-012)

    Spec: F03 DE-04. AC: US-02/AC-01. FT-anchor: FT-014. BT-anchor: BT-010.
    """

    def __init__(self, fixture_path: str | None = None) -> None:
        # TODO US-02/AC-01: load timing fixture (tts-marks variant or forced-alignment variant)
        self._fixture_path = fixture_path

    def get_timing(self, audio: bytes, transcript: str) -> WordTimingResult:
        # TODO FT-014: route per fixture's source field
        raise NotImplementedError


# Public registry — used by the contract-test parametrization (T-08).
__all__ = [
    "OCRBackendFake",
    "NLPBackendFake",
    "DiacritizerBackendFake",
    "G2PBackendFake",
    "TTSBackendFake",
    "WordTimingProviderFake",
    "AdapterError",  # re-export so test modules can import from one place
]
