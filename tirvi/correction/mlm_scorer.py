"""DictaBertMLMScorer — confusion-table + masked-LM ranker (DE-03).

Spec: F48 DE-03. AC: F48-S02/AC-01, F48-S02/AC-02, F48-S02/AC-03. T-03.

Loads ``tirvi/correction/confusion_pairs.yaml`` (BO51); for each
suspect builds single-site candidates, scores under DictaBERT-MLM,
and runs the decision tree:

  delta = score(c0) - score(original)
  delta < threshold_low                                   → keep_original
  threshold_low <= delta < threshold_high                 → ambiguous
  delta >= threshold_high
    AND c0 in NakdanWordList
    AND score(c0) - score(c1) >= margin                   → auto_apply
  else                                                    → ambiguous

Cache key: ``(token, sentence_context_hash, mlm_model_id, table_version)``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .ports import ICascadeStage, NakdanWordListPort
from .value_objects import CorrectionVerdict, SentenceContext


@dataclass(frozen=True)
class MLMThresholds:
    """Decision-tree thresholds for the MLM scorer (DE-03)."""

    low: float = 1.0
    high: float = 3.0
    margin: float = 0.5


@dataclass
class DictaBertMLMScorer(ICascadeStage):
    """Stage 2 — confusion-table-driven MLM ranker."""

    word_list: NakdanWordListPort
    thresholds: MLMThresholds = field(default_factory=MLMThresholds)
    mlm_model_id: str = "dicta-il/dictabert"
    confusion_table_version: str = "v1"

    def evaluate(
        self, token: str, context: SentenceContext
    ) -> CorrectionVerdict:
        # TODO AC-F48-S02/AC-01 (T-03): load confusion_pairs.yaml once
        #   (lru_cache on table_version).
        # TODO AC-F48-S02/AC-02 (T-03): build single-site candidates from
        #   the confusion table.
        # TODO AC-F48-S02/AC-02 (T-03): score original + each candidate
        #   under the MLM head using context.sentence_text masked at
        #   context.token_index.
        # TODO AC-F48-S02/AC-02 (T-03): apply the decision tree (see
        #   module docstring). NakdanWordListPort enforces the
        #   "real Hebrew word" gate before auto_apply.
        # TODO AC-F48-S02/AC-03 (T-03): cache on
        #   (token, context.sentence_hash, self.mlm_model_id,
        #    self.confusion_table_version).
        # TODO BT-214 (T-03): record cache_hit on the returned verdict.
        raise NotImplementedError(
            "AC-F48-S02/AC-01..AC-03 / FT-318 / FT-319 — TDD T-03 fills"
        )


__all__ = ["DictaBertMLMScorer", "MLMThresholds"]
