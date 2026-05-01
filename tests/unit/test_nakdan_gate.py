"""T-02 — NakdanGate first-stage word-list filter (DE-02).

AC: F48-S01/AC-01, F48-S01/AC-02. FT-316, FT-317. BT-209, NT-04.
"""

from __future__ import annotations

import time

import pytest

from tests.unit.conftest import FakeNakdanWordList
from tirvi.correction.nakdan_gate import NakdanGate
from tirvi.correction.value_objects import SentenceContext


class TestNakdanGateSkipRules:
    """Skip rules ahead of word-list lookup."""

    def test_empty_token_returns_skip_empty(self, fake_word_list, sample_sentence_context):
        gate = NakdanGate(word_list=fake_word_list)
        assert gate.evaluate("", sample_sentence_context).verdict == "skip_empty"

    def test_short_token_returns_skip_short(self, fake_word_list, sample_sentence_context):
        gate = NakdanGate(word_list=fake_word_list)
        assert gate.evaluate("א", sample_sentence_context).verdict == "skip_short"

    def test_digit_token_returns_skip_non_hebrew(self, fake_word_list, sample_sentence_context):
        gate = NakdanGate(word_list=fake_word_list)
        assert gate.evaluate("123", sample_sentence_context).verdict == "skip_non_hebrew"

    def test_latin_token_returns_skip_non_hebrew(self, fake_word_list, sample_sentence_context):
        gate = NakdanGate(word_list=fake_word_list)
        assert gate.evaluate("abc", sample_sentence_context).verdict == "skip_non_hebrew"


class TestNakdanGateVerdictRules:
    """Happy / suspect paths (DE-02)."""

    def test_known_word_returns_pass(self, fake_word_list, sample_sentence_context):
        gate = NakdanGate(word_list=fake_word_list)
        assert gate.evaluate("שלום", sample_sentence_context).verdict == "pass"

    def test_unknown_word_returns_suspect(self, fake_word_list, sample_sentence_context):
        gate = NakdanGate(word_list=fake_word_list)
        assert gate.evaluate("מילה", sample_sentence_context).verdict == "suspect"


class TestNakdanGateCacheBehavior:
    """FT-317: p95 ≤ 5 ms — caching is the budget."""

    def test_cache_keyed_on_token_and_word_list_version(self, sample_sentence_context):
        calls: list[str] = []

        class CountingList:
            def is_known_word(self, t: str) -> bool:
                calls.append(t)
                return t == "שלום"

        gate = NakdanGate(word_list=CountingList(), word_list_version="v1")
        gate.evaluate("שלום", sample_sentence_context)
        gate.evaluate("שלום", sample_sentence_context)  # should hit cache
        assert len(calls) == 1  # is_known_word not called twice

    def test_cache_hit_flag_set_on_repeat_lookup(self, fake_word_list, sample_sentence_context):
        gate = NakdanGate(word_list=fake_word_list)
        gate.evaluate("שלום", sample_sentence_context)
        v2 = gate.evaluate("שלום", sample_sentence_context)
        assert v2.cache_hit is True

    @pytest.mark.slow
    def test_p95_under_5ms_for_1000_token_loop(self, fake_word_list, sample_sentence_context):
        gate = NakdanGate(word_list=fake_word_list)
        gate.evaluate("שלום", sample_sentence_context)  # warm cache
        times = []
        for _ in range(1000):
            t0 = time.perf_counter()
            gate.evaluate("שלום", sample_sentence_context)
            times.append((time.perf_counter() - t0) * 1000)
        times.sort()
        p95 = times[int(0.95 * 1000)]
        assert p95 <= 5.0, f"p95 = {p95:.3f} ms > 5 ms"
