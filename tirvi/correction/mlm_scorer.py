"""DictaBertMLMScorer — confusion-table + masked-LM ranker (DE-03).

Spec: F48 DE-03. AC: F48-S02/AC-01, F48-S02/AC-02, F48-S02/AC-03. T-03.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path

from .errors import ConfusionTableMissing
from .ports import ICascadeStage, NakdanWordListPort
from .value_objects import CorrectionVerdict, SentenceContext


def score_token_in_context(
    token: str, ctx: SentenceContext, model_id: str
) -> dict[str, float]:
    """Score original token and candidates via DictaBERT MLM.

    Returns {"original": score, candidate: score, ...}.
    Monkeypatched in unit tests to return deterministic scores.
    """
    raise NotImplementedError("Real DictaBERT MLM — monkeypatched in unit tests")


def _parse_table_line(line: str) -> tuple[str, str]:
    s = line.rstrip()
    if not s or s.startswith("#"):
        return "skip", ""
    if s.startswith("  - "):
        return "item", s[4:].strip()
    if not s.startswith(" ") and s.endswith(":"):
        return "key", s[:-1].strip()
    return "skip", ""


def _load_table(path: str) -> dict[str, list[str]]:
    p = Path(path)
    if not p.exists():
        raise ConfusionTableMissing(f"confusion_pairs.yaml not found: {p}")
    result: dict[str, list[str]] = {}
    current_key: str | None = None
    with p.open(encoding="utf-8") as f:
        for line in f:
            kind, value = _parse_table_line(line)
            if kind == "key":
                current_key = value
            elif kind == "item" and current_key is not None:
                result.setdefault(current_key, []).append(value)
    return result


@dataclass(frozen=True)
class MLMThresholds:
    low: float = 1.0
    high: float = 3.0
    margin: float = 0.5


@dataclass
class DictaBertMLMScorer(ICascadeStage):
    """Stage 2 — confusion-table-driven MLM ranker (DE-03)."""

    word_list: NakdanWordListPort
    confusion_table_path: str = "tirvi/correction/confusion_pairs.yaml"
    thresholds: MLMThresholds = field(default_factory=MLMThresholds)
    mlm_model_id: str = "dicta-il/dictabert"
    confusion_table_version: str = "v1"
    _cache: dict = field(default_factory=dict, init=False, repr=False, compare=False)
    _table: dict = field(default_factory=dict, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self._table = _load_table(self.confusion_table_path)

    def evaluate(self, token: str, context: SentenceContext) -> CorrectionVerdict:
        key = (token, context.sentence_hash, self.mlm_model_id, self.confusion_table_version)
        if key in self._cache:
            return dataclasses.replace(self._cache[key], cache_hit=True)
        verdict = self._compute(token, context)
        self._cache[key] = verdict
        return verdict

    def _compute(self, token: str, context: SentenceContext) -> CorrectionVerdict:
        candidates = tuple(self._table.get(token, []))
        if not candidates:
            return self._no_candidates(token)
        scores = score_token_in_context(token, context, self.mlm_model_id)
        ranked = self._rank(candidates, scores)
        if not ranked:
            return self._no_candidates(token)
        return self._apply_tree(token, candidates, ranked, scores)

    def _rank(
        self, candidates: tuple[str, ...], scores: dict[str, float]
    ) -> list[tuple[str, float]]:
        return sorted(
            ((c, scores[c]) for c in candidates if c in scores),
            key=lambda x: x[1],
            reverse=True,
        )

    def _second_score(self, ranked: list[tuple[str, float]]) -> float:
        return ranked[1][1] if len(ranked) > 1 else -float("inf")

    def _apply_tree(
        self,
        token: str,
        candidates: tuple[str, ...],
        ranked: list[tuple[str, float]],
        scores: dict[str, float],
    ) -> CorrectionVerdict:
        c0, c0_score = ranked[0]
        c1_score = self._second_score(ranked)
        delta = c0_score - scores.get("original", 0.0)
        t = self.thresholds
        if delta < t.low:
            return self._verdict(token, "keep_original", None, delta, candidates)
        if delta < t.high:
            return self._verdict(token, "ambiguous", None, delta, candidates)
        if not self.word_list.is_known_word(c0):
            return self._verdict(token, "ambiguous", None, delta, candidates)
        if c0_score - c1_score < t.margin:
            return self._verdict(token, "ambiguous", None, delta, candidates)
        return self._verdict(token, "auto_apply", c0, delta, candidates)

    def _verdict(
        self,
        token: str,
        name: str,
        corrected: str | None,
        delta: float,
        candidates: tuple[str, ...],
    ) -> CorrectionVerdict:
        return CorrectionVerdict(
            stage="mlm_scorer",
            verdict=name,
            original=token,
            corrected_or_none=corrected,
            candidates=candidates,
            score=delta,
        )

    def _no_candidates(self, token: str) -> CorrectionVerdict:
        return CorrectionVerdict(
            stage="mlm_scorer", verdict="keep_original", original=token
        )


__all__ = ["DictaBertMLMScorer", "MLMThresholds"]
