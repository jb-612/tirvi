"""Possessive-mappiq rule — research probe.

Detects sentences where the subject is a generic possessor
("every mother / every father / every parent ...") and biases
the candidate selection of a dative focus word toward the
mappiq-bearing variant (e.g., `לְיַלְדָּהּ` "to her child" over
`לְיַלְדָּה` "to a girl").

Status: not yet wired into the production Nakdan inference path.
Lives here so the bench script can import a stable, tested version.
"""
from __future__ import annotations

import re

_MAPPIQ = "ּ"
_PREFIX_MARKER = "|"

_POSSESSOR_TRIGGERS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bכל\s+(אם|אב|הורה|אישה|איש|בן|בת|אדם)\b"),
)


def _has_possessor_trigger(sentence: str) -> bool:
    return any(p.search(sentence) for p in _POSSESSOR_TRIGGERS)


def _stem(option: str) -> str:
    return option.split(_PREFIX_MARKER)[-1]


def _has_mappiq_on_final_he(option: str) -> bool:
    stem = _stem(option)
    return len(stem) >= 2 and stem[-2] == "ה" and stem[-1] == _MAPPIQ


def _first_mappiq_index(options: list[str]) -> int | None:
    for i, opt in enumerate(options, 1):
        if _has_mappiq_on_final_he(opt):
            return i
    return None


def apply_rule(sentence: str, focus: str, options: list[str]) -> int | None:
    """Return 1-based index of the preferred mappiq option, or None.

    None means "rule does not fire" (either no possessor trigger or no
    mappiq variant in the candidate list); the caller should fall through
    to the next stage.
    """
    if not _has_possessor_trigger(sentence):
        return None
    return _first_mappiq_index(options)
