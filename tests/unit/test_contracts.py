"""T-08 — adapter-contract harness tests (parametrized over the fake registry).

Spec: F03 DE-05.
AC: US-01/AC-01.
FT-anchors: FT-016.
BT-anchors: BT-009, BT-011.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestAssertAdapterContractRejectsBytes:
    """T-08: BT-009 — contract rejects adapters that return raw bytes."""

    def test_us_01_ac_01_bt_009_bytes_return_raises_schema_contract_error(self) -> None:
        # Given: a fake adapter whose ocr_pdf is patched to return b"raw bytes"
        # When:  assert_adapter_contract(adapter, OCRBackend) is invoked
        # Then:  SchemaContractError is raised
        # And:   the error message contains "must return OCRResult"
        pass

    def test_us_01_ac_01_bt_009_tts_bytes_return_raises_schema_contract_error(self) -> None:
        pass

    def test_us_02_ac_01_bt_009_word_timing_bytes_return_raises_schema_contract_error(
        self,
    ) -> None:
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestAssertAdapterContractRequiredFields:
    """T-08: FT-016 — contract asserts every required result field is present."""

    def test_us_01_ac_01_ft_016_missing_provider_raises_schema_contract_error(self) -> None:
        pass

    def test_us_01_ac_01_ft_016_missing_confidence_raises_schema_contract_error(self) -> None:
        # confidence: float | None — None is legitimate, but the field MUST exist
        pass


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestAssertAdapterContractParametrizedOverFakes:
    """T-08: BT-011 — contract runs against every fake (catches schema drift)."""

    def test_us_01_ac_01_bt_011_all_fakes_pass_contract(self) -> None:
        # Given: the full fake registry from tirvi.fakes
        # When:  assert_adapter_contract is called on each (fake, port) pair
        # Then:  no SchemaContractError is raised
        # NOTE: this runs after @test-mock-registry fills the fake bodies;
        # at scaffold time, every fake is NotImplementedError, so this is skipped.
        pass
