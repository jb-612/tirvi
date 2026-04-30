"""T-04 — port Protocol tests.

Spec: F03 DE-02.
AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-011, FT-016.
BT-anchors: BT-009.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPortsAreRuntimeCheckable:
    """T-04: every port is ``@runtime_checkable``."""

    def test_us_01_ac_01_ocr_backend_is_runtime_checkable(self) -> None:
        # Given: a class implementing ``ocr_pdf(pdf_bytes) -> OCRResult``
        # When:  ``isinstance(instance, OCRBackend)`` is evaluated
        # Then:  it returns True
        pass

    def test_us_01_ac_01_nlp_backend_is_runtime_checkable(self) -> None:
        pass

    def test_us_01_ac_01_diacritizer_backend_is_runtime_checkable(self) -> None:
        pass

    def test_us_01_ac_01_g2p_backend_is_runtime_checkable(self) -> None:
        pass

    def test_us_01_ac_01_tts_backend_is_runtime_checkable(self) -> None:
        pass

    def test_us_02_ac_01_word_timing_provider_is_runtime_checkable(self) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPortsHaveSingleMethod:
    """T-04: each port defines exactly one method (single-method contracts)."""

    def test_us_01_ac_01_ft_011_ocr_backend_has_only_ocr_pdf(self) -> None:
        pass

    def test_us_01_ac_01_nlp_backend_has_only_analyze(self) -> None:
        pass

    def test_us_01_ac_01_diacritizer_backend_has_only_diacritize(self) -> None:
        pass

    def test_us_01_ac_01_g2p_backend_has_only_grapheme_to_phoneme(self) -> None:
        pass

    def test_us_01_ac_01_tts_backend_has_only_synthesize(self) -> None:
        pass

    def test_us_02_ac_01_word_timing_provider_has_only_get_timing(self) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPortReturnTypesAreResultObjects:
    """T-04: BT-009 — port methods return result types, never bytes."""

    def test_us_01_ac_01_bt_009_ocr_backend_return_annotation_is_ocr_result(self) -> None:
        # Given: introspection of OCRBackend.ocr_pdf via typing.get_type_hints
        # Then:  return annotation is OCRResult, not bytes
        pass

    def test_us_01_ac_01_bt_009_tts_backend_return_annotation_is_tts_result(self) -> None:
        pass

    def test_us_02_ac_01_bt_009_word_timing_provider_return_annotation_is_word_timing_result(
        self,
    ) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestPortsAreSync:
    """Pre-flight decision: F03 ports are sync Protocols (no async def)."""

    def test_us_01_ac_01_no_port_method_is_async(self) -> None:
        # Given: introspection of every port's only method
        # Then:  inspect.iscoroutinefunction returns False
        pass
