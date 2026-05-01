"""T-01 — port runtime checks for the F48 correction cascade.

Spec: F48 DE-01.
AC: F48-S01/AC-01, F48-S02/AC-02, F48-S03/AC-01, F48-S04/AC-01.

Scaffold — TDD T-01 fills bodies. All tests skipped at scaffold time.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestPortRuntimeCheckable:
    """All four F48 ports MUST be runtime_checkable Protocols (T-01)."""

    def test_icascadestage_is_runtime_checkable(self):
        # Given: tirvi.correction.ports.ICascadeStage
        # When:  isinstance(NakdanGate(...), ICascadeStage) is checked
        # Then:  resolves True without importing the concrete class
        pass

    def test_nakdan_word_list_port_is_runtime_checkable(self):
        # Given: tirvi.correction.ports.NakdanWordListPort
        # When:  isinstance check against a duck-typed fake
        # Then:  True
        pass

    def test_llm_client_port_is_runtime_checkable(self):
        # AC-F48-S03/AC-01: LLM is behind a port (ADR-029)
        pass

    def test_feedback_read_port_is_runtime_checkable(self):
        # AC-F48-S05/AC-01: feedback access is behind a port
        pass


class TestCorrectionVerdictShape:
    """BO52 surface: AC-F48-S01/AC-01 / AC-F48-S04/AC-01."""

    def test_verdict_is_frozen_dataclass(self):
        pass

    def test_verdict_carries_all_bo52_fields(self):
        # stage, verdict, original, corrected_or_none, score, candidates,
        # mode, cache_hit, reason, model_versions, prompt_template_version
        pass

    def test_verdict_default_factory_for_model_versions(self):
        pass


class TestSentenceContextShape:
    """Cache-key inputs (DE-03 / DE-04 / ADR-034)."""

    def test_sentence_context_is_frozen(self):
        pass

    def test_sentence_context_has_sentence_hash(self):
        pass
