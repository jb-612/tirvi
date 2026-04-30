"""Port Protocols for every pipeline stage (F03 DE-02).

Every port is single-method, ``@runtime_checkable``, and sync. Adapters may
wrap async I/O internally; the Protocol surface stays sync (pre-flight
decision, ADR-014).

Vendor-import boundary (F03 DE-06): no vendor SDK types appear in any port
signature. Return types are :mod:`tirvi.results` only — never raw ``bytes``
(BT-009).
"""

from typing import Protocol, runtime_checkable

from .results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
    OCRResult,
    TTSResult,
    WordTimingResult,
)


@runtime_checkable
class OCRBackend(Protocol):
    """Port for OCR adapters (Tesseract, Document AI, …).

    Invariants (named, TDD fills):
      - INV-PORT-OCR-001 (FT-011, BT-009): returns :class:`OCRResult`, never ``bytes``

    Spec: F03 DE-02. AC: US-01/AC-01.
    """

    def ocr_pdf(self, pdf_bytes: bytes) -> OCRResult:  # pragma: no cover — Protocol
        ...


@runtime_checkable
class NLPBackend(Protocol):
    """Port for Hebrew tokenization + POS adapters (DictaBERT, YAP, …).

    Invariants (named, TDD fills):
      - INV-PORT-NLP-001 (FT-011): returns :class:`NLPResult` with Hebrew UD tokens (F17)

    Spec: F03 DE-02. AC: US-01/AC-01.
    """

    def analyze(self, text: str, lang: str) -> NLPResult:  # pragma: no cover — Protocol
        ...


@runtime_checkable
class DiacritizerBackend(Protocol):
    """Port for nikud-insertion adapters (Dicta-Nakdan, …).

    Invariants (named, TDD fills):
      - INV-PORT-DIA-001 (FT-011): returns :class:`DiacritizationResult` with NFC→NFD nikud (F19)

    Spec: F03 DE-02. AC: US-01/AC-01.
    """

    def diacritize(self, text: str) -> DiacritizationResult:  # pragma: no cover — Protocol
        ...


@runtime_checkable
class G2PBackend(Protocol):
    """Port for grapheme-to-phoneme adapters (Phonikud, …).

    Invariants (named, TDD fills):
      - INV-PORT-G2P-001 (FT-011): returns :class:`G2PResult` with IPA/SAMPA per F20

    Spec: F03 DE-02. AC: US-01/AC-01.
    """

    def grapheme_to_phoneme(self, text: str, lang: str) -> G2PResult:  # pragma: no cover — Protocol
        ...


@runtime_checkable
class TTSBackend(Protocol):
    """Port for TTS adapters (Google Wavenet, Chirp-3-HD, …).

    Invariants (named, TDD fills):
      - INV-PORT-TTS-001 (FT-012, BT-009): returns :class:`TTSResult`, never ``bytes``
      - INV-PORT-TTS-002 (FT-013): ``word_marks is None`` is legitimate (mark-less providers)

    Spec: F03 DE-02. AC: US-01/AC-01.
    """

    def synthesize(self, ssml: str, voice: str) -> TTSResult:  # pragma: no cover — Protocol
        ...


@runtime_checkable
class WordTimingProvider(Protocol):
    """Port for word-timing adapters (TTSEmittedTimingAdapter, ForcedAlignmentAdapter).

    Coordinator implementation lives in :mod:`tirvi.word_timing_provider`.

    Invariants (named, TDD fills):
      - INV-PORT-WT-001 (FT-014, BT-012): returns :class:`WordTimingResult`
        with ``source`` recording which adapter produced the timings (ADR-015)

    Spec: F03 DE-03. AC: US-02/AC-01.
    """

    def get_timing(
        self, audio: bytes, transcript: str
    ) -> WordTimingResult:  # pragma: no cover — Protocol
        ...
