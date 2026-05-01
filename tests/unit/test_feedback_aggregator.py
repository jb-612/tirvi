"""T-08 — FeedbackAggregator (DE-08).

AC: F48-S05/AC-01..AC-04. FT-325. BT-211, BT-215, BT-220.
INV-CCS-006. NT-01.

Scaffold — TDD T-08 fills bodies.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="scaffold — /tdd fills")


class TestGroupingByOcrAndExpected:
    """AC-F48-S05/AC-02."""

    def test_groups_share_ocr_and_expected(self):
        pass

    def test_different_expected_yields_different_group(self):
        pass


class TestPerShaCap:
    """INV-CCS-006 / BT-220 — per-sha contribution capped at 1."""

    def test_multiple_rows_same_sha_count_as_one(self):
        # FT-325 — anti-spam
        pass

    def test_distinct_shas_count_correctly(self):
        pass


class TestThresholdGating:
    """AC-F48-S05/AC-03 — distinct_shas >= 3 emits suggestion."""

    def test_below_threshold_emits_nothing(self):
        pass

    def test_at_threshold_emits_one_suggestion(self):
        pass

    def test_above_threshold_emits_one_per_group(self):
        pass


class TestNeverAutoApply:
    """biz F48-R1-2: engineer-gated, never auto-applies."""

    def test_run_writes_to_rule_suggestions_json_only(self, tmp_path):
        # AC-F48-S05/AC-04
        pass

    def test_no_promotion_to_active_confusion_table(self):
        pass


class TestRulePromotedEventEmission:
    """AC-F48-S05/AC-03 — RulePromoted domain event surface."""

    def test_emit_rule_promoted_carries_support_count_and_distinct_shas(self):
        pass


class TestUserRejectionReadAtInit:
    """BT-211 — cascade reads user rejections at init to revert."""

    def test_user_rejections_loaded_from_feedback_db(self):
        # BT-215
        pass


class TestConfusionTableMissing:
    """NT-01 — surfaced via cascade init, not aggregator."""

    def test_missing_confusion_table_raises_typed_error(self):
        # ConfusionTableMissing
        pass
