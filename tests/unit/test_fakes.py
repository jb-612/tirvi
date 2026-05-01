"""T-06 + T-07 — fake registry tests.

Spec: F03 DE-04.
AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-012, FT-013, FT-014, FT-015.
BT-anchors: BT-010, BT-011.

Note: these tests pin the *shape* of the fakes. Fixture loading + canned
result wiring lands when ``@test-mock-registry`` runs after Gate 4.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestFakesImplementPorts:
    """T-06/T-07: every fake satisfies its port via runtime_checkable isinstance."""

    def test_us_01_ac_01_ocr_backend_fake_is_ocr_backend(self) -> None:
        pass

    def test_us_01_ac_01_nlp_backend_fake_is_nlp_backend(self) -> None:
        pass

    def test_us_01_ac_01_diacritizer_backend_fake_is_diacritizer_backend(self) -> None:
        pass

    def test_us_01_ac_01_g2p_backend_fake_is_g2p_backend(self) -> None:
        pass

    def test_us_01_ac_01_tts_backend_fake_is_tts_backend(self) -> None:
        pass

    def test_us_02_ac_01_word_timing_provider_fake_is_word_timing_provider(self) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills (filled by @test-mock-registry)")
class TestFakeDeterminism:
    """T-06: FT-015 — fakes return identical results across N calls."""

    def test_us_01_ac_01_ft_015_ocr_fake_is_deterministic(self) -> None:
        # Given: an OCRBackendFake with a happy-path fixture
        # When:  ocr_pdf is called 5 times with the same input
        # Then:  every result is identical (==)
        pass

    def test_us_01_ac_01_nlp_fake_is_deterministic(self) -> None:
        pass

    def test_us_01_ac_01_diacritizer_fake_is_deterministic(self) -> None:
        pass

    def test_us_01_ac_01_g2p_fake_is_deterministic(self) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills (filled by @test-mock-registry)")
class TestTtsFakeMarksVariants:
    """T-07: TTSBackendFake supports both marks-present and marks-absent fixtures."""

    def test_us_01_ac_01_ft_012_marks_present_fixture_returns_word_marks(self) -> None:
        # Given: a TTSBackendFake loaded with a marks-present (Wavenet-like) fixture
        # When:  synthesize is called
        # Then:  result.word_marks is a non-empty list[WordMark]
        pass

    def test_us_01_ac_01_ft_013_marks_absent_fixture_returns_word_marks_none(self) -> None:
        # Given: a TTSBackendFake loaded with a marks-absent (Chirp-3-HD-like) fixture
        # When:  synthesize is called
        # Then:  result.word_marks is None
        pass


@pytest.mark.skip(reason="scaffold — TDD fills (filled by @test-mock-registry)")
class TestWordTimingFakeRoutesPerSource:
    """T-07: WordTimingProviderFake routes per ``WordTimingResult.source`` field."""

    def test_us_02_ac_01_ft_014_tts_marks_fixture_returns_source_tts_marks(self) -> None:
        pass

    def test_us_02_ac_01_ft_014_forced_alignment_fixture_returns_source_forced_alignment(
        self,
    ) -> None:
        pass


class TestG2PFakeWholeTextEmission:
    """T-08 (ADR-028 §Migration step 4): G2PBackendFake emits whole-text IPA
    as a single ``["fake-ipa"]`` element, mirroring the production Phonikud
    adapter's whole-text contract instead of per-token entries.
    """

    def test_us_01_ac_01_g2p_fake_emits_single_element_phonemes_list(self) -> None:
        from tirvi.fakes import G2PBackendFake
        from tirvi.results import G2PResult

        fake = G2PBackendFake()
        result = fake.grapheme_to_phoneme("שָׁלוֹם", lang="he")

        assert isinstance(result, G2PResult)
        assert len(result.phonemes) == 1
        assert result.phonemes == ["fake-ipa"]


@pytest.mark.skip(reason="scaffold — TDD fills (filled by @test-mock-registry)")
class TestFailureModeFixtures:
    """T-06/T-07: BT-010 — every fake covers ≥ 1 documented failure mode."""

    def test_us_01_ac_01_bt_010_ocr_fake_failure_fixture_raises_typed_error(self) -> None:
        pass

    def test_us_01_ac_01_bt_010_nlp_fake_failure_fixture_raises_typed_error(self) -> None:
        pass

    def test_us_01_ac_01_bt_010_diacritizer_fake_failure_fixture_raises_typed_error(
        self,
    ) -> None:
        pass

    def test_us_01_ac_01_bt_010_g2p_fake_failure_fixture_raises_typed_error(self) -> None:
        pass

    def test_us_01_ac_01_bt_010_tts_fake_failure_fixture_raises_typed_error(self) -> None:
        pass

    def test_us_02_ac_01_bt_010_word_timing_fake_failure_fixture_raises_typed_error(
        self,
    ) -> None:
        pass
