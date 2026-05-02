"""ADR-040 — OllamaLLMReviewer emits ambiguous verdict on uncertainty.

When the LLM's parsed response carries `chosen: null` AND `alternatives:
[...]` of length ≥ 2, the reviewer emits a CorrectionVerdict with
`verdict="ambiguous"` and populates the new `alternatives_retained`
field. Anti-hallucination still applies — every entry in alternatives
must be in the input candidates list.

Closes part of GitHub issue #28.
"""
from __future__ import annotations

import pytest

from tests.unit.conftest import FakeLLMClient
from tirvi.correction.domain.policies import AntiHallucinationPolicy
from tirvi.correction.llm_reviewer import OllamaLLMReviewer


RESP_AMBIGUOUS = (
    '{"verdict":"AMBIGUOUS","chosen":null,'
    '"alternatives":["שלום","שלוּם"],'
    '"reason":"two readings linguistically valid"}'
)
RESP_AMBIGUOUS_HALLUCINATED = (
    '{"verdict":"AMBIGUOUS","chosen":null,'
    '"alternatives":["שלום","NOT_IN_CANDIDATES"],'
    '"reason":"..."}'
)
RESP_AMBIGUOUS_TOO_FEW = (
    '{"verdict":"AMBIGUOUS","chosen":null,'
    '"alternatives":["שלום"],'
    '"reason":"only one alternative — should not flag ambiguous"}'
)


@pytest.fixture
def prompt_dir(tmp_path):
    d = tmp_path / "prompts"
    d.mkdir()
    (d / "v1.txt").write_text(
        "Fix {original} in '{sentence}'. Options: {candidates}", encoding="utf-8"
    )
    (d / "_meta.yaml").write_text(
        'prompt_template_version: "v2-uncertain"\n', encoding="utf-8"
    )
    return d


@pytest.fixture
def reviewer_two_cands(fake_word_list, fake_llm_client, prompt_dir):
    return OllamaLLMReviewer(
        llm=fake_llm_client,
        anti_hallucination=AntiHallucinationPolicy(word_list=fake_word_list),
        candidates=("שלום", "שלוּם"),
        prompt_template_path=str(prompt_dir / "v1.txt"),
    )


class TestAmbiguousVerdict:
    def test_ambiguous_response_emits_ambiguous_verdict(
        self, reviewer_two_cands, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = RESP_AMBIGUOUS
        v = reviewer_two_cands.evaluate("שלום", sample_sentence_context)
        assert v.verdict == "ambiguous"
        assert v.corrected_or_none is None
        assert v.alternatives_retained == ("שלום", "שלוּם")

    def test_ambiguous_verdict_carries_reason(
        self, reviewer_two_cands, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = RESP_AMBIGUOUS
        v = reviewer_two_cands.evaluate("שלום", sample_sentence_context)
        assert "linguistically valid" in (v.reason or "")

    def test_ambiguous_with_hallucinated_alternative_falls_back_to_keep_original(
        self, reviewer_two_cands, fake_llm_client, sample_sentence_context
    ):
        """Anti-hallucination on alternatives — every entry must be in candidates."""
        fake_llm_client.canned_response = RESP_AMBIGUOUS_HALLUCINATED
        v = reviewer_two_cands.evaluate("שלום", sample_sentence_context)
        assert v.verdict == "keep_original"
        assert v.alternatives_retained == ()

    def test_single_alternative_does_not_flag_ambiguous(
        self, reviewer_two_cands, fake_llm_client, sample_sentence_context
    ):
        """An alternatives list of len < 2 is meaningless; treat as keep_original."""
        fake_llm_client.canned_response = RESP_AMBIGUOUS_TOO_FEW
        v = reviewer_two_cands.evaluate("שלום", sample_sentence_context)
        assert v.verdict == "keep_original"
        assert v.alternatives_retained == ()


class TestBackwardsCompat:
    def test_legacy_ok_response_still_keep_original(
        self, reviewer_two_cands, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = '{"verdict":"OK","chosen":null,"reason":"fine"}'
        v = reviewer_two_cands.evaluate("שלום", sample_sentence_context)
        assert v.verdict == "keep_original"
        assert v.alternatives_retained == ()

    def test_legacy_replace_response_still_apply(
        self, reviewer_two_cands, fake_llm_client, sample_sentence_context
    ):
        fake_llm_client.canned_response = '{"verdict":"REPLACE","chosen":"שלום","reason":"fix"}'
        v = reviewer_two_cands.evaluate("שלום_orig", sample_sentence_context)
        assert v.verdict == "apply"
        assert v.corrected_or_none == "שלום"
        assert v.alternatives_retained == ()


class TestVerdictDataclass:
    """Verify the new field on CorrectionVerdict itself."""

    def test_default_alternatives_retained_is_empty_tuple(self):
        from tirvi.correction.value_objects import CorrectionVerdict
        v = CorrectionVerdict(stage="llm_reviewer", verdict="apply", original="x")
        assert v.alternatives_retained == ()

    def test_explicit_alternatives_retained_field(self):
        from tirvi.correction.value_objects import CorrectionVerdict
        v = CorrectionVerdict(
            stage="llm_reviewer", verdict="ambiguous", original="x",
            alternatives_retained=("a", "b"),
        )
        assert v.alternatives_retained == ("a", "b")
