"""POC demo pipeline: PDF bytes → audio + timing + page JSON artefacts.

Wires OCR → block segmentation → normalization → NLP → diacritization →
G2P → reading plan → SSML → TTS → artefact write.

Spec: PLAN-POC.md "demo orchestrator".
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import struct
import wave
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from tirvi.ports import DiacritizerBackend, G2PBackend, NLPBackend, OCRBackend, TTSBackend
from tirvi.results import (
    DiacritizationResult,
    G2PResult,
    NLPResult,
    OCRPage,
    OCRResult,
    OCRWord,
    TTSResult,
    WordMark,
)

_POC_VOICE = "he-IL-Wavenet-D"


@dataclass
class PipelineDeps:
    """Adapter set for the POC pipeline (injectable for tests)."""

    ocr: OCRBackend
    nlp: NLPBackend
    dia: DiacritizerBackend
    g2p: G2PBackend
    tts: TTSBackend
    rasterize: Callable[[bytes, int], list[Any]]  # (pdf_bytes, dpi) -> [PIL.Image]


def run_pipeline(
    pdf_bytes: bytes,
    output_base: Path,
    deps: PipelineDeps | None = None,
    *,
    voice: str = _POC_VOICE,
) -> dict[str, Any]:
    """Run the full POC pipeline and write artefacts to ``output_base/<sha>/``.

    Returns ``{"sha": str, "drafts_dir": Path}``.
    """
    if deps is None:
        deps = _make_deps()

    from tirvi.blocks.aggregation import build_blocks
    from tirvi.blocks.page_stats import compute_page_stats
    from tirvi.normalize.passthrough import normalize_text
    from tirvi.normalize.ocr_corrections import correct_final_letters
    from tirvi.plan.aggregates import ReadingPlan
    from tirvi.ssml.builder import build_page_ssml

    ocr_result = deps.ocr.ocr_pdf(pdf_bytes)
    words = ocr_result.pages[0].words

    stats = compute_page_stats(words)
    blocks = build_blocks(words, stats)
    normalized = normalize_text(words)

    # Post-OCR correction: fix common Hebrew final-letter misreads (ס→ם etc.)
    raw_tokens = normalized.text.split()
    corrected_tokens = correct_final_letters(raw_tokens)
    corrected_text = " ".join(corrected_tokens)

    nlp_result = deps.nlp.analyze(corrected_text, lang="he")
    dia_result = deps.dia.diacritize(corrected_text)
    g2p_result = deps.g2p.grapheme_to_phoneme(dia_result.diacritized_text, lang="he")

    plan = ReadingPlan.from_inputs(
        page_id="page-1",
        blocks=tuple(blocks),
        normalized=normalized,
        nlp_result=nlp_result,
        diacritization=dia_result,
        g2p_result=g2p_result,
    )

    sha = hashlib.sha256(plan.to_json().encode()).hexdigest()[:16]
    drafts_dir = output_base / sha
    drafts_dir.mkdir(parents=True, exist_ok=True)

    images = deps.rasterize(pdf_bytes, 300)
    images[0].save(str(drafts_dir / "page-1.png"))

    tts_result = deps.tts.synthesize(build_page_ssml(plan), voice=voice)

    (drafts_dir / "audio.mp3").write_bytes(tts_result.audio_bytes)
    (drafts_dir / "audio.json").write_text(
        json.dumps(_build_audio_json(tts_result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (drafts_dir / "page.json").write_text(
        json.dumps(
            plan.to_page_json(ocr_result, page_image_url="page-1.png"),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {"sha": sha, "drafts_dir": drafts_dir}


def _build_audio_json(tts_result: TTSResult) -> dict[str, Any]:
    marks: list[WordMark] = tts_result.word_marks or []
    timings = []
    for i, mark in enumerate(marks):
        start_s = mark.start_ms / 1000.0
        if i + 1 < len(marks):
            end_s: float | None = marks[i + 1].start_ms / 1000.0
        elif tts_result.audio_duration_s is not None:
            end_s = tts_result.audio_duration_s
        else:
            end_s = start_s + 0.2
        timings.append({"mark_id": mark.mark_id, "start_s": start_s, "end_s": end_s})
    return {"timings": timings}


def make_stub_deps() -> PipelineDeps:
    """Return a PipelineDeps wired with local stubs (no ML packages needed).

    Useful for ``uv run scripts/run_demo.py --stubs`` to verify the full
    pipeline wiring and player UI without the Docker ML environment.
    """
    return PipelineDeps(
        ocr=_StubOCR(),
        nlp=_StubNLP(),
        dia=_StubDia(),
        g2p=_StubG2P(),
        tts=_StubTTS(),
        rasterize=_stub_rasterize,
    )


def make_poc_deps() -> PipelineDeps:
    """Return PipelineDeps for the POC demo: real OCR + Dia + G2P + TTS, stub NLP.

    Per ADR-025, Nakdan diacritization runs against the Dicta REST API.
    Per ADR-028, Phonikud G2P is wired via PhonikudG2PAdapter (whole-text
    IPA from ``phonemize()``). DictaBERT NLP stays stubbed (model
    unavailable in the POC environment); Wavenet handles synthesis.
    """
    from tirvi.adapters.nakdan.adapter import DictaNakdanAdapter
    from tirvi.adapters.phonikud.adapter import PhonikudG2PAdapter
    from tirvi.adapters.tesseract.adapter import TesseractOCRAdapter
    from tirvi.adapters.wavenet.adapter import WavenetTTSAdapter

    def _rasterize(pdf_bytes: bytes, dpi: int) -> list[Any]:
        from tirvi.adapters.tesseract.rasterizer import rasterize_pdf
        return rasterize_pdf(pdf_bytes, dpi)

    return PipelineDeps(
        ocr=TesseractOCRAdapter(),
        nlp=_StubNLP(),
        dia=DictaNakdanAdapter(),
        g2p=PhonikudG2PAdapter(),
        tts=WavenetTTSAdapter(),
        rasterize=_rasterize,
    )


def _make_deps() -> PipelineDeps:
    from tirvi.adapters.dictabert.adapter import DictaBERTAdapter
    from tirvi.adapters.nakdan.adapter import DictaNakdanAdapter
    from tirvi.adapters.phonikud.adapter import PhonikudG2PAdapter
    from tirvi.adapters.tesseract.adapter import TesseractOCRAdapter
    from tirvi.adapters.tesseract.rasterizer import rasterize_pdf
    from tirvi.adapters.wavenet.adapter import WavenetTTSAdapter

    return PipelineDeps(
        ocr=TesseractOCRAdapter(),
        nlp=DictaBERTAdapter(),
        dia=DictaNakdanAdapter(),
        g2p=PhonikudG2PAdapter(),
        tts=WavenetTTSAdapter(),
        rasterize=rasterize_pdf,
    )


# ---------------------------------------------------------------------------
# Stub adapter implementations (no vendor packages)
# ---------------------------------------------------------------------------

_STUB_WORDS = [
    OCRWord(text="הבחינה", bbox=(820, 50, 940, 72), confidence=0.95),
    OCRWord(text="בחשבונאות", bbox=(660, 50, 815, 72), confidence=0.95),
    OCRWord(text="מועד", bbox=(940, 90, 1010, 112), confidence=0.92),
    OCRWord(text="א'", bbox=(870, 90, 935, 112), confidence=0.90),
    OCRWord(text="שנת", bbox=(790, 90, 865, 112), confidence=0.92),
    OCRWord(text="תשפ\"ה", bbox=(700, 90, 785, 112), confidence=0.88),
]


class _StubOCR:
    def ocr_pdf(self, pdf_bytes: bytes) -> OCRResult:
        return OCRResult(provider="stub-ocr", pages=[OCRPage(words=list(_STUB_WORDS))])


class _StubNLP:
    def analyze(self, text: str, lang: str) -> NLPResult:
        return NLPResult(provider="stub-nlp", tokens=[], confidence=None)


class _StubDia:
    def diacritize(self, text: str) -> DiacritizationResult:
        return DiacritizationResult(provider="stub-dia", diacritized_text=text, confidence=None)


class _StubG2P:
    def grapheme_to_phoneme(self, text: str, lang: str) -> G2PResult:
        return G2PResult(provider="stub-g2p", phonemes=[], confidence=None)


class _StubTTS:
    def synthesize(self, ssml: str, voice: str) -> TTSResult:
        mark_ids = re.findall(r'<mark name="([^"]+)"', ssml)
        marks = [
            WordMark(mark_id=mid, start_ms=i * 500, end_ms=(i + 1) * 500)
            for i, mid in enumerate(mark_ids)
        ]
        duration_s = len(marks) * 0.5 + 0.5
        return TTSResult(
            provider="stub-tts",
            audio_bytes=_silent_wav(duration_s),
            codec="wav",
            voice_meta={"voice": voice, "tts_marks_truncated": False},
            word_marks=marks or None,
            audio_duration_s=duration_s,
        )


def _silent_wav(duration_s: float) -> bytes:
    """Generate a minimal silent mono WAV using only stdlib."""
    buf = io.BytesIO()
    nframes = max(1, int(22050 * duration_s))
    with wave.open(buf, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        wf.writeframes(b"\x00\x00" * nframes)
    return buf.getvalue()


def _blank_png() -> bytes:
    """Generate a minimal 1×1 white RGB PNG using only stdlib."""

    def _chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\xFF\xFF\xFF")  # filter=None, R=255 G=255 B=255
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


class _StubPage:
    def save(self, path: str, **kwargs: Any) -> None:
        Path(path).write_bytes(_blank_png())


def _stub_rasterize(pdf_bytes: bytes, dpi: int) -> list[Any]:
    return [_StubPage()]
