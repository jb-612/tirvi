"""T-04b — OllamaLLMReviewer domain wrapper (DE-04).

AC: F48-S03/AC-01, F48-S03/AC-03. FT-320, FT-322. BT-217.
NT-02, NT-03, NT-05. INV-CCS-002.
"""

from __future__ import annotations

import pytest

from tests.unit.conftest import FakeNakdanWordList, FakeLLMClient
from tirvi.correction.domain.policies import AntiHallucinationPolicy, PerPageLLMCapPolicy
from tirvi.correction.llm_reviewer import OllamaLLMReviewer
from tirvi.correction.value_objects import SentenceContext


RESP_OK = '{"verdict":"OK","chosen":null,"reason":"fine"}'
RESP_REPLACE = '{"verdict":"REPLACE","chosen":"שלום","reason":"fix"}'
RESP_BAD = "not-json"


@pytest.fixture
def prompt_dir(tmp_path):
    d = tmp_path / "prompts"
    d.mkdir()
    (d / "v1.txt").write_text(
        "Fix {original} in '{sentence}'. Options: {candidates}", encoding="utf-8"
    )
    (d / "_meta.yaml").write_text('prompt_template_version: "v1-test"\n', encoding="utf-8")
    return d


@pytest.fixture
def reviewer(fake_word_list, fake_llm_client, prompt_dir):
    return OllamaLLMReviewer(
        llm=fake_llm_client,
        anti_hallucination=AntiHallucinationPolicy(word_list=fake_word_list),
        candidates=("שלום",),
        prompt_template_path=str(prompt_dir / "v1.txt"),
    )


class TestPromptBuilding:
    """AC-F48-S03/AC-01: prompt built from template with variable substitution."""

    def test_prompt_substitutes_original_into_llm_call(
        self, reviewer, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = RESP_OK
        reviewer.evaluate("שלוֹם", sample_sentence_context)
        assert "שלוֹם" in fake_llm_client.calls[0]["prompt"]

    def test_prompt_template_version_loaded_from_meta_yaml(self, reviewer, sample_sentence_context, fake_llm_client):
        fake_llm_client.canned_response = RESP_OK
        reviewer.evaluate("x", sample_sentence_context)
        assert reviewer.prompt_template_version == "v1-test"


class TestVerdictParsing:
    """NT-02: parse {verdict, chosen, reason}; one re-prompt on failure."""

    def test_ok_verdict_returns_keep_original(
        self, reviewer, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = RESP_OK
        v = reviewer.evaluate("שלוֹם", sample_sentence_context)
        assert v.verdict == "keep_original"

    def test_replace_verdict_with_valid_chosen_returns_apply(
        self, reviewer, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = RESP_REPLACE
        v = reviewer.evaluate("שלוֹם", sample_sentence_context)
        assert v.verdict == "apply"
        assert v.corrected_or_none == "שלום"

    def test_parse_failure_retries_once(
        self, reviewer, fake_llm_client, sample_sentence_context
    ):
        responses = iter([RESP_BAD, RESP_OK])
        fake_llm_client.canned_response = None
        fake_llm_client.generate = lambda p, m, t, s: next(responses)
        reviewer.evaluate("שלוֹם", sample_sentence_context)
        assert len(fake_llm_client.calls) == 0  # direct lambda, not via default generate

    def test_second_parse_failure_returns_keep_original(
        self, reviewer, fake_llm_client, sample_sentence_context
    ):
        calls: list[int] = []

        def bad_generate(prompt, model_id, temperature, seed):
            calls.append(1)
            return RESP_BAD

        fake_llm_client.generate = bad_generate
        v = reviewer.evaluate("שלוֹם", sample_sentence_context)
        assert v.verdict == "keep_original"
        assert len(calls) == 2  # tried twice


class TestAntiHallucinationGuard:
    """INV-CCS-002 / AC-F48-S03/AC-03."""

    def test_chosen_not_in_candidates_rejects_correction(
        self, prompt_dir, fake_word_list, sample_sentence_context
    ):
        llm = FakeLLMClient(canned_response='{"verdict":"REPLACE","chosen":"unknown","reason":"x"}')
        rv = OllamaLLMReviewer(
            llm=llm,
            anti_hallucination=AntiHallucinationPolicy(word_list=fake_word_list),
            candidates=("שלום",),  # "unknown" is NOT in candidates
            prompt_template_path=str(prompt_dir / "v1.txt"),
        )
        v = rv.evaluate("שלוֹם", sample_sentence_context)
        assert v.verdict == "keep_original"
        assert v.reason == "anti_hallucination_reject"

    def test_chosen_not_in_word_list_rejects_correction(
        self, prompt_dir, sample_sentence_context
    ):
        llm = FakeLLMClient(canned_response='{"verdict":"REPLACE","chosen":"מחוץ","reason":"x"}')
        rv = OllamaLLMReviewer(
            llm=llm,
            anti_hallucination=AntiHallucinationPolicy(word_list=FakeNakdanWordList(known=set())),
            candidates=("מחוץ",),  # in candidates but NOT in word list
            prompt_template_path=str(prompt_dir / "v1.txt"),
        )
        v = rv.evaluate("x", sample_sentence_context)
        assert v.verdict == "keep_original"
        assert v.reason == "anti_hallucination_reject"

    def test_anti_hallucination_reject_stamps_reason(
        self, reviewer, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = '{"verdict":"REPLACE","chosen":"invented","reason":"x"}'
        v = reviewer.evaluate("שלוֹם", sample_sentence_context)
        assert v.reason == "anti_hallucination_reject"


class TestPerPageLLMCapShortCircuit:
    """BT-F-05: when cap reached, return keep_original without calling LLM."""

    def test_cap_reached_skips_llm_call(
        self, prompt_dir, fake_word_list, fake_llm_client, sample_sentence_context
    ):
        rv = OllamaLLMReviewer(
            llm=fake_llm_client,
            anti_hallucination=AntiHallucinationPolicy(word_list=fake_word_list),
            cap_policy=PerPageLLMCapPolicy(cap=1),
            candidates=("שלום",),
            prompt_template_path=str(prompt_dir / "v1.txt"),
        )
        fake_llm_client.canned_response = RESP_OK
        rv.evaluate("t1", sample_sentence_context)  # uses the 1 allowed call
        rv.evaluate("t2", sample_sentence_context)  # cap reached
        assert len(fake_llm_client.calls) == 1

    def test_cap_reached_returns_keep_original_with_reason(
        self, prompt_dir, fake_word_list, fake_llm_client, sample_sentence_context
    ):
        rv = OllamaLLMReviewer(
            llm=fake_llm_client,
            anti_hallucination=AntiHallucinationPolicy(word_list=fake_word_list),
            cap_policy=PerPageLLMCapPolicy(cap=0),
            candidates=("שלום",),
            prompt_template_path=str(prompt_dir / "v1.txt"),
        )
        v = rv.evaluate("t1", sample_sentence_context)
        assert v.verdict == "keep_original"
        assert v.reason == "llm_call_cap_reached"


class TestLLMCacheKey:
    """ADR-034: reviewer-level verdict cache keyed on sorted candidates."""

    def test_cache_hit_records_cache_hit_flag(
        self, reviewer, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = RESP_OK
        reviewer.evaluate("שלוֹם", sample_sentence_context)
        v2 = reviewer.evaluate("שלוֹם", sample_sentence_context)
        assert v2.cache_hit is True

    def test_different_candidate_order_yields_same_key(
        self, prompt_dir, fake_word_list, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = RESP_OK
        rv1 = OllamaLLMReviewer(
            llm=fake_llm_client,
            anti_hallucination=AntiHallucinationPolicy(word_list=fake_word_list),
            candidates=("א", "ב"),
            prompt_template_path=str(prompt_dir / "v1.txt"),
        )
        rv2 = OllamaLLMReviewer(
            llm=fake_llm_client,
            anti_hallucination=AntiHallucinationPolicy(word_list=fake_word_list),
            candidates=("ב", "א"),  # reversed order
            prompt_template_path=str(prompt_dir / "v1.txt"),
        )
        rv1.evaluate("x", sample_sentence_context)
        rv1.candidates = ("ב", "א")  # swap order — cache key uses sorted so same
        v2 = rv1.evaluate("x", sample_sentence_context)
        assert v2.cache_hit is True
