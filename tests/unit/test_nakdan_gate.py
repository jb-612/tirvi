"""T-02 — NakdanGate first-stage word-list filter (DE-02).

AC: F48-S01/AC-01, F48-S01/AC-02. FT-316, FT-317. BT-209, NT-04.

Scaffold — TDD T-02 fills bodies.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestNakdanGateSkipRules:
    """Skip rules ahead of word-list lookup."""

    def test_empty_token_returns_skip_empty(self):
        # Given: NakdanGate with any word list
        # When:  evaluate("", ctx)
        # Then:  verdict == "skip_empty"  (NT-04)
        pass

    def test_short_token_returns_skip_short(self):
        # BT-F-03: len(token) < 2 → skip_short
        pass

    def test_digit_token_returns_skip_non_hebrew(self):
        # AC-F48-S01/AC-01
        pass

    def test_latin_token_returns_skip_non_hebrew(self):
        pass


class TestNakdanGateVerdictRules:
    """Happy / suspect paths (DE-02)."""

    def test_known_word_returns_pass(self):
        # AC-F48-S01/AC-01
        pass

    def test_unknown_word_returns_suspect(self):
        # AC-F48-S01/AC-02 — forwarded to MLM stage
        pass


class TestNakdanGateCacheBehavior:
    """FT-317: p95 ≤ 5 ms — caching is the budget."""

    def test_cache_keyed_on_token_and_word_list_version(self):
        pass

    def test_cache_hit_flag_set_on_repeat_lookup(self):
        # BT-214 (cache hit recording)
        pass

    @pytest.mark.slow
    def test_p95_under_5ms_for_1000_token_loop(self):
        # FT-317 — performance gate. May only run with --slow.
        pass
