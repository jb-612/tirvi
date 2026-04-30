"""Result-object value types for every pipeline stage (F03 DE-01).

Each result is a frozen ``@dataclass`` carrying a ``provider`` stamp (FT-traceability)
and ``confidence: float | None`` — **never** ``0.0``, per biz S01: distinguishes
"no signal available" from "low confidence score".

Schema versioning is contract-test-only per ADR-014; no numeric ``schema_version``
field until the first breaking change.
"""

from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# OCR
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OCRWord:
    """One word extracted by an OCR backend.

    Invariants (named, TDD fills):
      - INV-OCR-W-001 (FT-011): bbox is (x0, y0, x1, y1), pixel coords post-deskew
      - INV-OCR-W-002 (FT-011): conf in [0.0, 1.0] or None when unavailable
    """

    text: str
    bbox: tuple[int, int, int, int]
    conf: float | None = None
    lang_hint: str | None = None


@dataclass(frozen=True)
class OCRPage:
    """One page of OCR output. Invariant: ``words`` reading-order RTL-corrected."""

    words: list[OCRWord]
    lang_hints: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class OCRResult:
    """Output of :class:`tirvi.ports.OCRBackend`. Spec: F03 DE-01.

    Invariants (named, TDD fills):
      - INV-OCR-001 (FT-011, BT-009): result is :class:`OCRResult`, never ``bytes``
      - INV-OCR-002 (biz S01): ``confidence is None`` when provider is silent — never ``0.0``
    """

    provider: str
    pages: list[OCRPage]
    confidence: float | None = None


# ---------------------------------------------------------------------------
# NLP
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NLPToken:
    """One token from a Hebrew UD tokenizer (per F17). Invariants set by F17."""

    text: str
    pos: str | None = None
    lemma: str | None = None


@dataclass(frozen=True)
class NLPResult:
    """Output of :class:`tirvi.ports.NLPBackend`. Spec: F03 DE-01."""

    provider: str
    tokens: list[NLPToken]
    confidence: float | None = None


# ---------------------------------------------------------------------------
# Diacritization
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DiacritizationResult:
    """Output of :class:`tirvi.ports.DiacritizerBackend`. Spec: F03 DE-01.

    Nikud NFC-then-NFD ordering pinned by F19; not enforced here.
    """

    provider: str
    diacritized_text: str
    confidence: float | None = None


# ---------------------------------------------------------------------------
# G2P
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class G2PResult:
    """Output of :class:`tirvi.ports.G2PBackend`. Spec: F03 DE-01.

    Phoneme alphabet (IPA / SAMPA) pinned by F20; not enforced here.
    """

    provider: str
    phonemes: list[str]
    confidence: float | None = None


# ---------------------------------------------------------------------------
# TTS
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WordMark:
    """One ``<mark>`` emitted by an SSML-aware TTS provider.

    Invariants (named, TDD fills):
      - INV-MARK-001 (FT-012): ``start_ms <= end_ms``
      - INV-MARK-002 (FT-014): ``mark_id`` matches PlanToken.id from F22
    """

    mark_id: str
    start_ms: int
    end_ms: int
    text: str | None = None


@dataclass(frozen=True)
class TTSResult:
    """Output of :class:`tirvi.ports.TTSBackend`. Spec: F03 DE-01.

    Invariants (named, TDD fills):
      - INV-TTS-001 (FT-012, BT-009): result is :class:`TTSResult`, never ``bytes``
      - INV-TTS-002 (FT-013): ``word_marks is None`` is a legitimate value
        (Chirp-3-HD-like providers); F30 detects via ``voice_meta["tts_marks_truncated"]``
      - INV-TTS-003 (post-review C8, F30 DE-02): ``audio_duration_s is None``
        when the upstream API does not report duration (Wavenet behavior is
        inconsistent); used to derive last-token end time
    """

    provider: str
    audio_bytes: bytes
    codec: str
    voice_meta: dict[str, str | bool | None]
    word_marks: list[WordMark] | None = None
    audio_duration_s: float | None = None
    confidence: float | None = None


# ---------------------------------------------------------------------------
# WordTiming (DE-03 — dual-source: tts-marks | forced-alignment)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WordTiming:
    """One word's timing, irrespective of source.

    Invariants (named, TDD fills):
      - INV-WT-001 (FT-014): ``start_s <= end_s`` when both present
      - INV-WT-002 (post-review C2, F30 DE-05): ``end_s`` may be ``None`` for tail
        tokens after a truncated-mark alignment
    """

    mark_id: str
    start_s: float
    end_s: float | None = None


@dataclass(frozen=True)
class WordTimingResult:
    """Output of :class:`tirvi.ports.WordTimingProvider`. Spec: F03 DE-01, DE-03.

    The ``source`` field records which adapter produced the timings (ADR-015 fallback).

    Invariants (named, TDD fills):
      - INV-WTR-001 (FT-014): ``len(timings) == len(transcript_tokens)`` unless
        the TTS-marks adapter set ``tts_marks_truncated`` in upstream voice_meta
      - INV-WTR-002 (BT-012): ``source == "forced-alignment"`` when fallback fired
    """

    provider: str
    source: Literal["tts-marks", "forced-alignment"]
    timings: list[WordTiming]
    audio_duration_s: float | None = None
    tts_marks_truncated: bool = False
    confidence: float | None = None
