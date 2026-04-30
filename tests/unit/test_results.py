"""T-02 + T-03 — result dataclass tests.

Spec: F03 DE-01, DE-03.
AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-011, FT-012, FT-013, FT-014.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestResultDataclassesAreFrozen:
    """T-02: every result type is immutable (frozen=True)."""

    def test_us_01_ac_01_ft_011_ocr_result_is_frozen(self) -> None:
        # Given: an OCRResult instance
        # When:  a field assignment is attempted
        # Then:  ``FrozenInstanceError`` is raised
        pass

    def test_us_01_ac_01_nlp_result_is_frozen(self) -> None:
        pass

    def test_us_01_ac_01_diacritization_result_is_frozen(self) -> None:
        pass

    def test_us_01_ac_01_g2p_result_is_frozen(self) -> None:
        pass

    def test_us_01_ac_01_ft_012_tts_result_is_frozen(self) -> None:
        pass

    def test_us_02_ac_01_ft_014_word_timing_result_is_frozen(self) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestResultProviderField:
    """T-02: every result carries a ``provider: str`` stamp (FT-traceability)."""

    def test_us_01_ac_01_ft_011_ocr_result_carries_provider(self) -> None:
        # Given: an OCRResult with provider="tesseract"
        # Then:  result.provider == "tesseract"
        pass

    def test_us_01_ac_01_ft_012_tts_result_carries_provider(self) -> None:
        pass

    def test_us_02_ac_01_ft_014_word_timing_result_carries_provider(self) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestConfidenceNullability:
    """T-02: ``confidence: float | None`` — biz S01: never default to ``0.0``."""

    def test_us_01_ac_01_ft_011_confidence_defaults_to_none_not_zero(self) -> None:
        # Given: a result built without a confidence kwarg
        # Then:  result.confidence is None  # never 0.0
        pass

    def test_us_01_ac_01_confidence_accepts_explicit_none(self) -> None:
        pass

    def test_us_01_ac_01_confidence_accepts_float(self) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestTtsResultAudioDurationField:
    """T-02: TTSResult.audio_duration_s — post-review C8 (F30 DE-02)."""

    def test_us_01_ac_01_ft_012_tts_result_audio_duration_s_defaults_to_none(self) -> None:
        # Wavenet inconsistency: API may not report duration → None is legitimate
        pass

    def test_us_01_ac_01_ft_012_tts_result_audio_duration_s_accepts_float(self) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestTtsResultMarksAbsentIsLegitimate:
    """T-02: TTSResult.word_marks=None is a legitimate value (FT-013)."""

    def test_us_01_ac_01_ft_013_tts_result_word_marks_can_be_none(self) -> None:
        # Given: a Chirp-3-HD-like provider that emits no marks
        # Then:  TTSResult(word_marks=None) constructs successfully
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestWordTimingResultSourceLiteral:
    """T-03: WordTimingResult.source is a Literal (DE-03, FT-014)."""

    def test_us_02_ac_01_ft_014_source_accepts_tts_marks(self) -> None:
        pass

    def test_us_02_ac_01_ft_014_source_accepts_forced_alignment(self) -> None:
        pass

    def test_us_02_ac_01_ft_014_source_rejects_arbitrary_string(self) -> None:
        # Given: a static type-checker run (mypy strict)
        # Then:  source="invalid" is rejected at type-check time
        # NOTE: runtime accepts any str (Python Literal is documentation);
        # this test pins the mypy contract via reveal_type or similar.
        pass
