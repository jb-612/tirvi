"""T-08 — FeedbackAggregator (DE-08).

AC: F48-S05/AC-01..AC-04. FT-325. BT-211, BT-215, BT-220.
INV-CCS-006. NT-01.
"""

from __future__ import annotations

import json

import pytest

from tests.unit.conftest import FakeFeedbackReader, FakeNakdanWordList
from tirvi.correction.errors import ConfusionTableMissing
from tirvi.correction.feedback_aggregator import (
    DEFAULT_DISTINCT_SHA_THRESHOLD,
    FeedbackAggregator,
)
from tirvi.correction.value_objects import SentenceContext, UserRejection


def _rejection(ocr="bad", expected="good", sha="sha1"):
    return UserRejection(
        ocr_word=ocr, system_chose=expected, expected=expected,
        persona_role="teacher", sentence_context_hash="h", draft_sha=sha,
    )


def _agg(rejections_by_sha, output_path, threshold=DEFAULT_DISTINCT_SHA_THRESHOLD):
    return FeedbackAggregator(
        feedback=FakeFeedbackReader(rejections_by_sha),
        shas=tuple(rejections_by_sha.keys()),
        output_path=output_path,
        distinct_sha_threshold=threshold,
    )


class TestGroupingByOcrAndExpected:
    """AC-F48-S05/AC-02."""

    def test_groups_share_ocr_and_expected(self, tmp_path):
        data = {
            "sha1": [_rejection("bad", "good", "sha1")],
            "sha2": [_rejection("bad", "good", "sha2")],
            "sha3": [_rejection("bad", "good", "sha3")],
        }
        suggestions = _agg(data, tmp_path / "s.json").run()
        assert len(suggestions) == 1
        assert suggestions[0].ocr_word == "bad"
        assert suggestions[0].expected == "good"

    def test_different_expected_yields_different_group(self, tmp_path):
        data = {
            "sha1": [_rejection("bad", "fix1", "sha1")],
            "sha2": [_rejection("bad", "fix2", "sha2")],
        }
        suggestions = _agg(data, tmp_path / "s.json", threshold=1).run()
        assert len(suggestions) == 2


class TestPerShaCap:
    """INV-CCS-006 / BT-220 — per-sha contribution capped at 1."""

    def test_multiple_rows_same_sha_count_as_one(self, tmp_path):
        data = {
            "sha1": [
                _rejection("bad", "good", "sha1"),
                _rejection("bad", "good", "sha1"),
            ],
        }
        suggestions = _agg(data, tmp_path / "s.json", threshold=1).run()
        assert len(suggestions) == 1
        assert suggestions[0].distinct_shas == 1

    def test_distinct_shas_count_correctly(self, tmp_path):
        data = {
            "sha1": [_rejection("bad", "good", "sha1")],
            "sha2": [_rejection("bad", "good", "sha2")],
            "sha3": [_rejection("bad", "good", "sha3")],
        }
        suggestions = _agg(data, tmp_path / "s.json").run()
        assert suggestions[0].distinct_shas == 3


class TestThresholdGating:
    """AC-F48-S05/AC-03 — distinct_shas >= 3 emits suggestion."""

    def test_below_threshold_emits_nothing(self, tmp_path):
        data = {
            "sha1": [_rejection("bad", "good", "sha1")],
            "sha2": [_rejection("bad", "good", "sha2")],
        }
        suggestions = _agg(data, tmp_path / "s.json").run()
        assert len(suggestions) == 0

    def test_at_threshold_emits_one_suggestion(self, tmp_path):
        data = {
            "sha1": [_rejection("bad", "good", "sha1")],
            "sha2": [_rejection("bad", "good", "sha2")],
            "sha3": [_rejection("bad", "good", "sha3")],
        }
        suggestions = _agg(data, tmp_path / "s.json").run()
        assert len(suggestions) == 1

    def test_above_threshold_emits_one_per_group(self, tmp_path):
        data = {
            "sha1": [_rejection("bad", "good", "sha1"), _rejection("bad2", "ok", "sha1")],
            "sha2": [_rejection("bad", "good", "sha2"), _rejection("bad2", "ok", "sha2")],
            "sha3": [_rejection("bad", "good", "sha3"), _rejection("bad2", "ok", "sha3")],
        }
        suggestions = _agg(data, tmp_path / "s.json").run()
        assert len(suggestions) == 2


class TestNeverAutoApply:
    """biz F48-R1-2: engineer-gated, never auto-applies."""

    def test_run_writes_to_rule_suggestions_json_only(self, tmp_path):
        data = {
            "sha1": [_rejection("bad", "good", "sha1")],
            "sha2": [_rejection("bad", "good", "sha2")],
            "sha3": [_rejection("bad", "good", "sha3")],
        }
        out = tmp_path / "rule_suggestions.json"
        _agg(data, out).run()
        assert out.exists()
        rows = json.loads(out.read_text(encoding="utf-8"))
        assert len(rows) == 1

    def test_no_promotion_to_active_confusion_table(self, tmp_path):
        data = {
            "sha1": [_rejection()],
            "sha2": [_rejection(sha="sha2")],
            "sha3": [_rejection(sha="sha3")],
        }
        confusion_path = tmp_path / "confusion_pairs.yaml"
        _agg(data, tmp_path / "s.json").run()
        assert not confusion_path.exists()


class TestRulePromotedEventEmission:
    """AC-F48-S05/AC-03 — RulePromoted domain event surface."""

    def test_emit_rule_promoted_carries_support_count_and_distinct_shas(self, tmp_path):
        from tirvi.correction.domain.events import RulePromoted
        data = {
            "sha1": [_rejection()],
            "sha2": [_rejection(sha="sha2")],
            "sha3": [_rejection(sha="sha3")],
        }
        agg = _agg(data, tmp_path / "s.json")
        suggestions = agg.run()
        event = agg._emit_rule_promoted(suggestions[0])
        assert isinstance(event, RulePromoted)
        assert event.support_count == 3
        assert event.distinct_shas == 3


class TestUserRejectionReadAtInit:
    """BT-211 — cascade reads user rejections at init to revert."""

    def test_user_rejections_loaded_from_feedback_db(self, tmp_path):
        data = {"sha1": [_rejection("word", "fix", "sha1")]}
        agg = FeedbackAggregator(
            feedback=FakeFeedbackReader(data),
            shas=("sha1",),
            output_path=tmp_path / "s.json",
            distinct_sha_threshold=1,
        )
        suggestions = agg.run()
        assert len(suggestions) == 1
        assert suggestions[0].ocr_word == "word"


class TestConfusionTableMissing:
    """NT-01 — surfaced via cascade init, not aggregator."""

    def test_missing_confusion_table_raises_typed_error(self, tmp_path):
        from tirvi.correction.mlm_scorer import DictaBertMLMScorer
        with pytest.raises(ConfusionTableMissing):
            DictaBertMLMScorer(
                word_list=FakeNakdanWordList(),
                confusion_table_path=str(tmp_path / "nonexistent.yaml"),
            )
