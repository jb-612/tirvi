"""T-04b — OllamaLLMReviewer domain wrapper (DE-04).

AC: F48-S03/AC-01, F48-S03/AC-03. FT-320, FT-322. BT-217.
NT-02, NT-03, NT-05. INV-CCS-002.

Scaffold — TDD T-04b fills bodies.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestPromptBuilding:
    """AC-F48-S03/AC-01: prompt from prompts/he_reviewer/v1.txt."""

    def test_prompt_substitutes_sentence_original_candidates(self):
        pass

    def test_prompt_template_version_loaded_from_meta_yaml(self):
        pass


class TestVerdictParsing:
    """NT-02: parse {verdict, chosen, reason}; one re-prompt on failure."""

    def test_ok_verdict_returns_keep_original(self):
        pass

    def test_replace_verdict_with_valid_chosen_returns_apply(self):
        # AC-F48-S03/AC-01
        pass

    def test_parse_failure_retries_once(self):
        # NT-02 — one re-prompt
        pass

    def test_second_parse_failure_returns_keep_original(self):
        # NT-02
        pass


class TestAntiHallucinationGuard:
    """INV-CCS-002 / AC-F48-S03/AC-03."""

    def test_chosen_not_in_candidates_rejects_correction(self):
        # NT-03
        pass

    def test_chosen_not_in_word_list_rejects_correction(self):
        # NT-05
        pass

    def test_anti_hallucination_reject_emits_correction_rejected(self):
        # AC-F48-S03/AC-03
        pass


class TestPerPageLLMCapShortCircuit:
    """BT-F-05: when cap reached, return keep_original without calling LLM."""

    def test_cap_reached_skips_llm_call(self):
        pass

    def test_cap_reached_returns_keep_original_with_reason(self):
        pass


class TestLLMCacheKey:
    """ADR-034 cache key shape — sha256(model || version || sentence_hash || sorted(candidates))."""

    def test_cache_hit_records_cache_hit_flag(self):
        pass

    def test_different_candidate_order_yields_same_key(self):
        # ADR-034 — sorted(candidates)
        pass
