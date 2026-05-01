"""NakdanGate — first-stage word-list filter (DE-02).

Spec: F48 DE-02. AC: F48-S01/AC-01, F48-S01/AC-02. T-02.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .ports import ICascadeStage, NakdanWordListPort
from .value_objects import CorrectionVerdict, SentenceContext


def _is_non_hebrew(token: str) -> bool:
    return any(ch.isdigit() or (ch.isalpha() and ch.isascii()) for ch in token)


@dataclass
class NakdanGate(ICascadeStage):
    """First-stage word-list filter (DE-02)."""

    word_list: NakdanWordListPort
    word_list_version: str = "unknown"
    _cache: dict = field(default_factory=dict, init=False, repr=False, compare=False)

    def evaluate(self, token: str, context: SentenceContext) -> CorrectionVerdict:
        if not token:
            return self._make(token, "skip_empty")
        if len(token) < 2:
            return self._make(token, "skip_short")
        if _is_non_hebrew(token):
            return self._make(token, "skip_non_hebrew")
        return self._lookup(token)

    def _lookup(self, token: str) -> CorrectionVerdict:
        key = (token, self.word_list_version)
        if key in self._cache:
            is_known = self._cache[key]
            cache_hit = True
        else:
            is_known = self.word_list.is_known_word(token)
            self._cache[key] = is_known
            cache_hit = False
        verdict = "pass" if is_known else "suspect"
        return CorrectionVerdict(
            stage="nakdan_gate", verdict=verdict, original=token, cache_hit=cache_hit
        )

    def _make(self, token: str, verdict: str) -> CorrectionVerdict:
        return CorrectionVerdict(stage="nakdan_gate", verdict=verdict, original=token)


__all__ = ["NakdanGate"]
