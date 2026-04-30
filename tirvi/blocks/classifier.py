"""F11 T-03 — heuristic block classifier (POC scope).

Spec: N01/F11 DE-03, DE-04. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-075, FT-076. BT-anchors: BT-051, BT-054.

Priority order: ``question_stem`` > ``heading`` > ``paragraph``. Confidence
< 0.6 falls back to ``paragraph`` per US-02/AC-01 (DE-04).
"""

from __future__ import annotations

import re

from tirvi.results import OCRWord

from .taxonomy import BlockType
from .value_objects import PageStats

# "שאלה" + optional whitespace + a digit. Curly quotes accepted.
_QUESTION_STEM_RE = re.compile(r"^\s*שאלה[\s ]+[\d]")
_HEADING_HEIGHT_RATIO = 1.5
_LOW_CONFIDENCE_THRESHOLD = 0.6


def classify_block(
    words: list[OCRWord],
    page_stats: PageStats,
) -> tuple[BlockType, float]:
    """Return ``(BlockType, confidence)`` for the given block words.

    Falls back to ``("paragraph", confidence)`` when confidence is below 0.6.
    """
    if _is_question_stem(words):
        return ("question_stem", 0.9)
    if _is_heading(words, page_stats):
        return ("heading", 0.7)
    return ("paragraph", 0.5)


def _is_question_stem(words: list[OCRWord]) -> bool:
    if not words:
        return False
    leading = " ".join(w.text for w in words[:3])
    return bool(_QUESTION_STEM_RE.match(leading))


def _is_heading(words: list[OCRWord], stats: PageStats) -> bool:
    if not words or stats.median_word_height <= 0:
        return False
    avg_height = sum(w.bbox[3] - w.bbox[1] for w in words) / len(words)
    return avg_height >= stats.median_word_height * _HEADING_HEIGHT_RATIO


def is_low_confidence(confidence: float) -> bool:
    return confidence < _LOW_CONFIDENCE_THRESHOLD
