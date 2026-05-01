"""T-03 — DictaBertMLMScorer (DE-03).

AC: F48-S02/AC-01, F48-S02/AC-02, F48-S02/AC-03. FT-318, FT-319, FT-328.
BT-214.

Scaffold — TDD T-03 fills bodies.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestConfusionTableLoad:
    """AC-F48-S02/AC-01: load confusion_pairs.yaml once (lru_cache)."""

    def test_confusion_table_loaded_lazily(self):
        pass

    def test_missing_confusion_table_raises_confusion_table_missing(self):
        # NT-01 — surfaced via cascade init
        pass


class TestSingleSiteCandidateGeneration:
    """AC-F48-S02/AC-02: single-site swap candidates (POC)."""

    def test_candidates_built_from_confusion_pairs(self):
        # Given: confusion table {ם↔ס, ן↔ו, ר↔ד}
        # When:  evaluate("סיוס", ctx)
        # Then:  candidates include "סיום"
        pass

    def test_no_candidates_when_no_confusion_chars(self):
        pass


class TestMlmDecisionTree:
    """AC-F48-S02/AC-02: thresholds (low=1.0, high=3.0, margin=0.5)."""

    def test_delta_below_low_returns_keep_original(self):
        pass

    def test_delta_in_band_returns_ambiguous(self):
        pass

    def test_delta_above_high_with_word_list_pass_returns_auto_apply(self):
        pass

    def test_delta_above_high_but_c0_not_in_word_list_returns_ambiguous(self):
        pass

    def test_margin_violation_demotes_auto_apply_to_ambiguous(self):
        # FT-319: score(c0) - score(c1) < margin
        pass


class TestMlmCacheBehavior:
    """AC-F48-S02/AC-03: cache key (token, sentence_hash, model_id, table_version)."""

    def test_cache_hit_recorded_on_verdict(self):
        # BT-214
        pass

    def test_different_sentence_hash_misses_cache(self):
        pass
