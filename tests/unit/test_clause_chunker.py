"""F53 T-01 / T-02 / T-03 — clause-split chunker.

`chunk_block_tokens(tokens, threshold=22) -> (fragments, breaks)` —
returns the input split at safe boundaries when over threshold, with
ADR-041 row #9 provenance entries for each break.

Spec: N02/F53 DE-01, DE-02, DE-03. AC: F53-S01/AC-01..S03/AC-01.
"""
from __future__ import annotations

from tirvi.plan.value_objects import PlanToken
from tirvi.ssml.chunker import (
    CONJUNCTION_LEXICON,
    DEFAULT_THRESHOLD,
    chunk_block_tokens,
)


def _t(text: str, idx: int = 0, pos: str | None = None) -> PlanToken:
    return PlanToken(
        id=f"b1-{idx}", text=text, src_word_indices=(idx,), pos=pos,
    )


# ----- T-01: token-count gate -----


class TestThresholdGate:
    def test_under_threshold_returns_single_fragment_no_breaks(self):
        tokens = [_t(f"word{i}", i) for i in range(10)]
        fragments, breaks = chunk_block_tokens(tokens, threshold=22)
        assert len(fragments) == 1
        assert fragments[0] == tokens
        assert breaks == []

    def test_at_threshold_does_not_split(self):
        tokens = [_t(f"w{i}", i) for i in range(22)]
        fragments, breaks = chunk_block_tokens(tokens, threshold=22)
        assert len(fragments) == 1
        assert breaks == []

    def test_default_threshold_is_22(self):
        # Per Q3 answer
        assert DEFAULT_THRESHOLD == 22

    def test_empty_token_list_returns_empty(self):
        fragments, breaks = chunk_block_tokens([], threshold=22)
        assert fragments == [[]]
        assert breaks == []


# ----- T-02: punctuation-based boundaries -----


class TestPunctuationBoundaries:
    def test_long_sentence_with_period_splits_after_period(self):
        # 30 tokens, with period at index 15 → split after token 15
        tokens = [_t(f"w{i}", i) for i in range(15)] + [_t(".", 15)] + [
            _t(f"w{i}", i) for i in range(16, 30)
        ]
        fragments, breaks = chunk_block_tokens(tokens, threshold=22)
        assert len(fragments) >= 2
        # First fragment ends with the period token
        assert fragments[0][-1].text == "."

    def test_split_at_comma_when_no_other_boundary(self):
        # 30 tokens, comma at index 14 — only safe boundary
        tokens = [_t(f"w{i}", i) for i in range(14)] + [_t(",", 14)] + [
            _t(f"w{i}", i) for i in range(15, 30)
        ]
        fragments, breaks = chunk_block_tokens(tokens, threshold=22)
        assert len(fragments) >= 2
        assert fragments[0][-1].text == ","

    def test_no_safe_boundary_emits_clause_split_skipped(self):
        # 30 tokens, no punctuation, no conjunction with SCONJ tag
        tokens = [_t(f"word{i}", i) for i in range(30)]
        fragments, breaks = chunk_block_tokens(tokens, threshold=22)
        assert len(fragments) == 1   # could not split
        assert len(breaks) == 1
        assert breaks[0]["kind"] == "clause_split_skipped"
        assert breaks[0]["reason"] == "no_safe_boundary"


# ----- T-02: conjunction-based boundaries (SCONJ guard) -----


class TestConjunctionBoundaries:
    def test_kivan_she_with_sconj_tag_triggers_split(self):
        # 30 tokens; "כיוון ש" at index 14 with SCONJ tag → split BEFORE it
        tokens = [_t(f"w{i}", i) for i in range(14)] + [
            _t("כיוון ש", 14, pos="SCONJ"),
        ] + [_t(f"w{i}", i) for i in range(15, 30)]
        fragments, breaks = chunk_block_tokens(tokens, threshold=22)
        assert len(fragments) >= 2
        # The conjunction token should START the second fragment, not end the first
        assert fragments[1][0].text == "כיוון ש"

    def test_conjunction_without_sconj_tag_is_skipped(self):
        # Same conjunction surface but POS is not SCONJ → NO split there
        tokens = [_t(f"w{i}", i) for i in range(14)] + [
            _t("כיוון ש", 14, pos="NOUN"),  # wrong POS — skip
        ] + [_t(f"w{i}", i) for i in range(15, 30)]
        fragments, breaks = chunk_block_tokens(tokens, threshold=22)
        # Falls through to "no safe boundary" since no punct either
        assert len(fragments) == 1
        assert breaks[0]["kind"] == "clause_split_skipped"

    def test_conjunction_lexicon_exposed_for_extension(self):
        assert "כיוון ש" in CONJUNCTION_LEXICON
        assert "מאחר ש" in CONJUNCTION_LEXICON


# ----- T-03: provenance entries -----


class TestProvenance:
    def test_punctuation_break_emits_provenance(self):
        tokens = [_t(f"w{i}", i) for i in range(15)] + [_t(".", 15)] + [
            _t(f"w{i}", i) for i in range(16, 30)
        ]
        _, breaks = chunk_block_tokens(tokens, threshold=22)
        # At least one clause_split entry
        splits = [b for b in breaks if b["kind"] == "clause_split"]
        assert len(splits) >= 1
        entry = splits[0]
        assert entry["reason"] == "punctuation"
        assert entry["adr_row"] == "ADR-041 #9"
        assert "at_token_index" in entry
        assert "fragment_word_count_after" in entry

    def test_conjunction_break_carries_lemma_in_reason(self):
        tokens = [_t(f"w{i}", i) for i in range(14)] + [
            _t("כיוון ש", 14, pos="SCONJ"),
        ] + [_t(f"w{i}", i) for i in range(15, 30)]
        _, breaks = chunk_block_tokens(tokens, threshold=22)
        splits = [b for b in breaks if b["kind"] == "clause_split"]
        assert len(splits) >= 1
        # reason field encodes "conjunction:<lemma>"
        assert any(s["reason"].startswith("conjunction:") for s in splits)

    def test_skipped_split_emits_provenance(self):
        tokens = [_t(f"w{i}", i) for i in range(30)]
        _, breaks = chunk_block_tokens(tokens, threshold=22)
        skipped = [b for b in breaks if b["kind"] == "clause_split_skipped"]
        assert len(skipped) == 1
        assert skipped[0]["reason"] == "no_safe_boundary"
        assert skipped[0]["word_count"] == 30
