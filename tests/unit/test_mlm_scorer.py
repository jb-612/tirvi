"""T-03 — DictaBertMLMScorer (DE-03).

AC: F48-S02/AC-01, F48-S02/AC-02, F48-S02/AC-03. FT-318, FT-319, FT-328.
BT-214.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.unit.conftest import FakeNakdanWordList
from tirvi.correction.errors import ConfusionTableMissing
from tirvi.correction.mlm_scorer import DictaBertMLMScorer
from tirvi.correction.value_objects import SentenceContext


def _write_table(tmp_path: Path, data: dict) -> str:
    p = tmp_path / "confusion_pairs.yaml"
    lines = []
    for key, candidates in data.items():
        lines.append(f"{key}:")
        for c in candidates:
            lines.append(f"  - {c}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


def _scorer(tmp_path, monkeypatch, mock_scores, known=frozenset(), token_map=None):
    """Helper: build a scorer with patched scoring and a two-candidate table."""
    token_map = token_map or {"שלום": ["שָׁלוֹם", "שַׁלוֹם"]}
    monkeypatch.setattr(
        "tirvi.correction.mlm_scorer.score_token_in_context",
        lambda token, ctx, model_id, candidates=(): mock_scores,
    )
    return DictaBertMLMScorer(
        confusion_table_path=_write_table(tmp_path, token_map),
        word_list=FakeNakdanWordList(known=set(known)),
    )


class TestConfusionTableLoad:
    """AC-F48-S02/AC-01: load confusion_pairs.yaml once."""

    def test_confusion_table_loaded_at_init(self, tmp_path, monkeypatch, sample_sentence_context):
        monkeypatch.setattr(
            "tirvi.correction.mlm_scorer.score_token_in_context",
            lambda token, ctx, model_id, candidates=(): {"original": 0.0},
        )
        table = _write_table(tmp_path, {"שלום": ["שָׁלוֹם"]})
        scorer = DictaBertMLMScorer(
            confusion_table_path=table,
            word_list=FakeNakdanWordList(known={"שָׁלוֹם"}),
        )
        assert scorer is not None

    def test_missing_confusion_table_raises_confusion_table_missing(self, tmp_path):
        with pytest.raises(ConfusionTableMissing):
            DictaBertMLMScorer(
                confusion_table_path=str(tmp_path / "nonexistent.yaml"),
                word_list=FakeNakdanWordList(),
            )


class TestSingleSiteCandidateGeneration:
    """AC-F48-S02/AC-02: single-site swap candidates."""

    def test_candidates_built_from_confusion_pairs(self, tmp_path, monkeypatch, sample_sentence_context):
        monkeypatch.setattr(
            "tirvi.correction.mlm_scorer.score_token_in_context",
            lambda token, ctx, model_id, candidates=(): {"original": 0.0, "סיום": 0.5},
        )
        scorer = DictaBertMLMScorer(
            confusion_table_path=_write_table(tmp_path, {"סיוס": ["סיום"]}),
            word_list=FakeNakdanWordList(known={"סיום"}),
        )
        verdict = scorer.evaluate("סיוס", sample_sentence_context)
        assert "סיום" in verdict.candidates

    def test_no_candidates_when_token_not_in_table(self, tmp_path, monkeypatch, sample_sentence_context):
        monkeypatch.setattr(
            "tirvi.correction.mlm_scorer.score_token_in_context",
            lambda token, ctx, model_id, candidates=(): {"original": 0.0},
        )
        scorer = DictaBertMLMScorer(
            confusion_table_path=_write_table(tmp_path, {"אחר": ["אחרת"]}),
            word_list=FakeNakdanWordList(),
        )
        verdict = scorer.evaluate("מילה", sample_sentence_context)
        assert verdict.candidates == ()
        assert verdict.verdict == "keep_original"


class TestMlmDecisionTree:
    """AC-F48-S02/AC-02: thresholds (low=1.0, high=3.0, margin=0.5)."""

    def test_delta_below_low_returns_keep_original(self, tmp_path, monkeypatch, sample_sentence_context):
        scorer = _scorer(
            tmp_path, monkeypatch,
            mock_scores={"original": 2.0, "שָׁלוֹם": 2.5},  # delta=0.5 < 1.0
            known={"שָׁלוֹם"},
        )
        assert scorer.evaluate("שלום", sample_sentence_context).verdict == "keep_original"

    def test_delta_in_band_returns_ambiguous(self, tmp_path, monkeypatch, sample_sentence_context):
        scorer = _scorer(
            tmp_path, monkeypatch,
            mock_scores={"original": 2.0, "שָׁלוֹם": 3.5},  # delta=1.5 in [1.0,3.0)
            known={"שָׁלוֹם"},
        )
        assert scorer.evaluate("שלום", sample_sentence_context).verdict == "ambiguous"

    def test_delta_above_high_with_word_list_pass_returns_auto_apply(
        self, tmp_path, monkeypatch, sample_sentence_context
    ):
        scorer = _scorer(
            tmp_path, monkeypatch,
            mock_scores={"original": 1.0, "שָׁלוֹם": 5.0, "שַׁלוֹם": 3.0},  # delta=4.0, margin=2.0
            known={"שָׁלוֹם", "שַׁלוֹם"},
        )
        v = scorer.evaluate("שלום", sample_sentence_context)
        assert v.verdict == "auto_apply"
        assert v.corrected_or_none == "שָׁלוֹם"

    def test_delta_above_high_but_c0_not_in_word_list_returns_ambiguous(
        self, tmp_path, monkeypatch, sample_sentence_context
    ):
        scorer = _scorer(
            tmp_path, monkeypatch,
            mock_scores={"original": 1.0, "שָׁלוֹם": 5.0},
            known=set(),  # שָׁלוֹם NOT in word list
        )
        assert scorer.evaluate("שלום", sample_sentence_context).verdict == "ambiguous"

    def test_margin_violation_demotes_auto_apply_to_ambiguous(
        self, tmp_path, monkeypatch, sample_sentence_context
    ):
        scorer = _scorer(
            tmp_path, monkeypatch,
            mock_scores={"original": 1.0, "שָׁלוֹם": 5.0, "שַׁלוֹם": 4.7},  # margin=0.3 < 0.5
            known={"שָׁלוֹם", "שַׁלוֹם"},
        )
        assert scorer.evaluate("שלום", sample_sentence_context).verdict == "ambiguous"


class TestMlmCacheBehavior:
    """AC-F48-S02/AC-03: cache key (token, sentence_hash, model_id, table_version)."""

    def test_cache_hit_recorded_on_verdict(self, tmp_path, monkeypatch, sample_sentence_context):
        scorer = _scorer(
            tmp_path, monkeypatch,
            mock_scores={"original": 2.0, "שָׁלוֹם": 2.5},
            known={"שָׁלוֹם"},
        )
        scorer.evaluate("שלום", sample_sentence_context)
        v2 = scorer.evaluate("שלום", sample_sentence_context)
        assert v2.cache_hit is True

    def test_different_sentence_hash_misses_cache(self, tmp_path, monkeypatch):
        scorer = _scorer(
            tmp_path, monkeypatch,
            mock_scores={"original": 2.0, "שָׁלוֹם": 2.5},
            known={"שָׁלוֹם"},
        )
        ctx1 = SentenceContext(sentence_text="foo", sentence_hash="hash1")
        ctx2 = SentenceContext(sentence_text="bar", sentence_hash="hash2")
        scorer.evaluate("שלום", ctx1)
        v2 = scorer.evaluate("שלום", ctx2)
        assert v2.cache_hit is False
