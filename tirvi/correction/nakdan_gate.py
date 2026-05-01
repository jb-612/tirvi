"""NakdanGate — first-stage word-list filter (DE-02).

Spec: F48 DE-02. AC: F48-S01/AC-01, F48-S01/AC-02. T-02.

Single-method ``ICascadeStage`` over an injected ``NakdanWordListPort``.

Skip rules (BT-F-03, NT-04, biz NT-04):
  - empty token             → ``skip_empty``
  - len < 2                 → ``skip_short``
  - digit / Latin character → ``skip_non_hebrew``

Verdict rules (DE-02):
  - known word              → ``pass``
  - unknown word            → ``suspect`` (forwarded to MLM stage)

Cache key: ``(token, word_list_version)``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ports import ICascadeStage, NakdanWordListPort
from .value_objects import CorrectionVerdict, SentenceContext


@dataclass
class NakdanGate(ICascadeStage):
    """First-stage word-list filter (DE-02)."""

    word_list: NakdanWordListPort
    word_list_version: str = "unknown"

    def evaluate(
        self, token: str, context: SentenceContext
    ) -> CorrectionVerdict:
        # TODO AC-F48-S01/AC-01 (T-02): apply skip rules first
        #   - if not token: return verdict="skip_empty"     (NT-04)
        #   - if len(token) < 2: return verdict="skip_short" (BT-F-03)
        #   - if any(ch.isdigit() or ch.isascii() for ch): return "skip_non_hebrew"
        # TODO AC-F48-S01/AC-01 (T-02): cache lookup on
        #   (token, self.word_list_version) via lru_cache helper.
        # TODO AC-F48-S01/AC-01 (T-02): if self.word_list.is_known_word(token):
        #   return verdict="pass" else verdict="suspect".
        # TODO FT-317 (T-02): keep p95 ≤ 5 ms — cache is the budget.
        raise NotImplementedError(
            "AC-F48-S01/AC-01 / FT-316 / FT-317 — TDD T-02 fills"
        )


__all__ = ["NakdanGate"]
