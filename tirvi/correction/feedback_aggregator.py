"""FeedbackAggregator — threshold-gated rule promotion suggestions (DE-08).

Spec: F48 DE-08. AC: F48-S05/AC-01..AC-04.
T-08.
"""

from __future__ import annotations

import dataclasses
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .domain.events import RulePromoted
from .domain.policies import PerShaContributionCapPolicy
from .ports import FeedbackReadPort

DEFAULT_DISTINCT_SHA_THRESHOLD: int = 3


@dataclass(frozen=True)
class RuleSuggestion:
    """One row in ``drafts/rule_suggestions.json`` (BO56).

    AC: F48-S05/AC-03, F48-S05/AC-04.
    """

    ocr_word: str
    expected: str
    support_count: int          # = distinct_shas (after per-sha cap)
    distinct_shas: int
    sample_sentence_hashes: tuple[str, ...] = ()


@dataclass
class FeedbackAggregator:
    """CLI entry point for the rule-promotion aggregator (DE-08)."""

    feedback: FeedbackReadPort
    shas: tuple[str, ...]
    output_path: Path
    cap_policy: PerShaContributionCapPolicy = field(default_factory=PerShaContributionCapPolicy)
    distinct_sha_threshold: int = DEFAULT_DISTINCT_SHA_THRESHOLD

    def run(self) -> tuple[RuleSuggestion, ...]:
        groups = self._collect_groups()
        suggestions = self._threshold_filter(groups)
        self._write(suggestions)
        return tuple(suggestions)

    def _collect_groups(self) -> dict[tuple[str, str], dict[str, int]]:
        groups: dict[tuple[str, str], dict[str, int]] = {}
        for sha in self.shas:
            for rejection in self.feedback.user_rejections(sha):
                if rejection.expected is None:
                    continue
                key = (rejection.ocr_word, rejection.expected)
                grp = groups.setdefault(key, {})
                grp[sha] = grp.get(sha, 0) + 1
        return groups

    def _threshold_filter(self, groups: dict) -> list[RuleSuggestion]:
        result = []
        for (ocr_word, expected), sha_counts in groups.items():
            distinct = self.cap_policy.cap_per_sha(sha_counts)
            if distinct >= self.distinct_sha_threshold:
                result.append(RuleSuggestion(
                    ocr_word=ocr_word, expected=expected,
                    support_count=distinct, distinct_shas=distinct,
                ))
        return result

    def _write(self, suggestions: list[RuleSuggestion]) -> None:
        doc = [dataclasses.asdict(s) for s in suggestions]
        tmp = self.output_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.output_path)

    def _emit_rule_promoted(self, sugg: RuleSuggestion) -> RulePromoted:
        return RulePromoted(
            ocr_word=sugg.ocr_word, expected=sugg.expected,
            support_count=sugg.support_count, distinct_shas=sugg.distinct_shas,
            occurred_at=datetime.utcnow(),
        )


__all__ = [
    "FeedbackAggregator",
    "RuleSuggestion",
    "DEFAULT_DISTINCT_SHA_THRESHOLD",
]
