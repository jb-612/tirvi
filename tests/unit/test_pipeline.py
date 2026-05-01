"""Tests for tirvi.pipeline — run_pipeline() and make_stub_deps().

All adapters are injected as mocks or stubs so no vendor packages are required.

Spec: PLAN-POC.md "demo orchestrator".
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tirvi.pipeline import PipelineDeps, run_pipeline
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


def _word(text: str = "שלום", x0: int = 10, y0: int = 20, x1: int = 60, y1: int = 40) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), conf=0.9)


def _fake_deps() -> PipelineDeps:
    word = _word()
    ocr_result = OCRResult(provider="test-ocr", pages=[OCRPage(words=[word])])

    mock_ocr = MagicMock()
    mock_ocr.ocr_pdf.return_value = ocr_result

    mock_nlp = MagicMock()
    mock_nlp.analyze.return_value = NLPResult(provider="test-nlp", tokens=[], confidence=None)

    mock_dia = MagicMock()
    mock_dia.diacritize.return_value = DiacritizationResult(
        provider="test-dia", diacritized_text="שָׁלוֹם", confidence=None
    )

    mock_g2p = MagicMock()
    mock_g2p.grapheme_to_phoneme.return_value = G2PResult(
        provider="test-g2p", phonemes=[], confidence=None
    )

    mark = WordMark(mark_id="b1-0", start_ms=100, end_ms=100)
    mock_tts = MagicMock()
    mock_tts.synthesize.return_value = TTSResult(
        provider="test-tts",
        audio_bytes=b"\xff\xfb\x10\x00" * 50,
        codec="mp3",
        voice_meta={"voice": "test", "tts_marks_truncated": False},
        word_marks=[mark],
        audio_duration_s=1.5,
    )

    mock_img = MagicMock()
    mock_rasterize = MagicMock(return_value=[mock_img])

    return PipelineDeps(
        ocr=mock_ocr,
        nlp=mock_nlp,
        dia=mock_dia,
        g2p=mock_g2p,
        tts=mock_tts,
        rasterize=mock_rasterize,
    )


class TestRunPipeline:
    def test_returns_sha_and_drafts_dir(self, tmp_path: Path) -> None:
        result = run_pipeline(b"fake-pdf", tmp_path, _fake_deps())
        assert isinstance(result["sha"], str)
        assert len(result["sha"]) == 16
        assert isinstance(result["drafts_dir"], Path)
        assert result["drafts_dir"].is_dir()

    def test_writes_audio_mp3(self, tmp_path: Path) -> None:
        result = run_pipeline(b"fake-pdf", tmp_path, _fake_deps())
        assert (result["drafts_dir"] / "audio.mp3").is_file()

    def test_writes_audio_json_with_timings(self, tmp_path: Path) -> None:
        result = run_pipeline(b"fake-pdf", tmp_path, _fake_deps())
        payload = json.loads((result["drafts_dir"] / "audio.json").read_text())
        assert "timings" in payload
        assert isinstance(payload["timings"], list)

    def test_timing_shape(self, tmp_path: Path) -> None:
        result = run_pipeline(b"fake-pdf", tmp_path, _fake_deps())
        payload = json.loads((result["drafts_dir"] / "audio.json").read_text())
        t = payload["timings"][0]
        assert "mark_id" in t
        assert "start_s" in t
        assert "end_s" in t

    def test_writes_page_json(self, tmp_path: Path) -> None:
        result = run_pipeline(b"fake-pdf", tmp_path, _fake_deps())
        payload = json.loads((result["drafts_dir"] / "page.json").read_text())
        assert "words" in payload
        assert "marks_to_word_index" in payload

    def test_timing_uses_audio_duration_for_last_mark(self, tmp_path: Path) -> None:
        result = run_pipeline(b"fake-pdf", tmp_path, _fake_deps())
        payload = json.loads((result["drafts_dir"] / "audio.json").read_text())
        last = payload["timings"][-1]
        assert last["end_s"] == pytest.approx(1.5)


class TestMakeStubDeps:
    def test_returns_pipeline_deps(self) -> None:
        from tirvi.pipeline import make_stub_deps
        deps = make_stub_deps()
        assert isinstance(deps, PipelineDeps)

    def test_stub_ocr_returns_words(self) -> None:
        from tirvi.pipeline import make_stub_deps
        deps = make_stub_deps()
        result = deps.ocr.ocr_pdf(b"any")
        assert isinstance(result, OCRResult)
        assert len(result.pages[0].words) > 0

    def test_stub_tts_marks_align_with_ssml(self) -> None:
        from tirvi.pipeline import make_stub_deps
        deps = make_stub_deps()
        ssml = '<speak xml:lang="he-IL"><mark name="b1-0"/>שלום <mark name="b1-1"/>עולם</speak>'
        res = deps.tts.synthesize(ssml, voice="stub")
        assert res.word_marks is not None
        assert [m.mark_id for m in res.word_marks] == ["b1-0", "b1-1"]

    def test_stub_pipeline_end_to_end(self, tmp_path: Path) -> None:
        from tirvi.pipeline import make_stub_deps
        result = run_pipeline(b"pdf", tmp_path, make_stub_deps())
        assert (result["drafts_dir"] / "audio.json").exists()
        assert (result["drafts_dir"] / "page.json").exists()


class TestMakePocDeps:
    def test_returns_pipeline_deps(self) -> None:
        from tirvi.pipeline import make_poc_deps
        deps = make_poc_deps()
        assert isinstance(deps, PipelineDeps)

    def test_nlp_is_stub(self) -> None:
        from tirvi.pipeline import _StubNLP, make_poc_deps
        deps = make_poc_deps()
        assert isinstance(deps.nlp, _StubNLP)

    def test_dia_is_real_nakdan_rest(self) -> None:
        # Per ADR-025 Nakdan now runs against the Dicta REST API.
        from tirvi.adapters.nakdan.adapter import DictaNakdanAdapter
        from tirvi.pipeline import make_poc_deps
        deps = make_poc_deps()
        assert isinstance(deps.dia, DictaNakdanAdapter)

    def test_rasterize_is_callable(self) -> None:
        from tirvi.pipeline import make_poc_deps
        deps = make_poc_deps()
        assert callable(deps.rasterize)

    def test_g2p_is_phonikud_adapter(self) -> None:
        # T-07 (ADR-028 §Migration step 3): make_poc_deps wires the real
        # PhonikudG2PAdapter, replacing the previous _StubG2P() placeholder.
        from tirvi.adapters.phonikud.adapter import PhonikudG2PAdapter
        from tirvi.pipeline import make_poc_deps
        deps = make_poc_deps()
        assert isinstance(deps.g2p, PhonikudG2PAdapter)
