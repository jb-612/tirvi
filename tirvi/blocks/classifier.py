"""F11 + F52 — heuristic block classifier.

Spec: N01/F11 DE-03/DE-04, N02/F52 DE-02. AC: F52-S01/AC-02, F52-S02/AC-01.
ADR-041 row #20 — provenance for confident non-fallback picks.

Priority order (first match wins):
    answer_blank  →  empty input  (highest signal — no words at all)
    instruction   →  starts with `הוראות / קרא בעיון / שים לב`
    datum         →  starts with `נתונים`
    multi_choice  →  ≥ 3 consecutive `א./ב./ג./ד.` letter prefixes
    question_stem →  starts with `שאלה N` (legacy F11 — kept)
    heading       →  word height ≥ 1.5× page modal  (legacy F11 — kept)
    paragraph     →  default for normal-height continuous prose
    mixed         →  short / unclassifiable blocks (F52 fallback per Q2)

The first three F52 cues fire BEFORE legacy heading/paragraph paths so
that an instruction block at large font is still classified as
instruction (the structural meaning), not heading (the visual meaning).
"""

from __future__ import annotations

import re

from tirvi.results import OCRWord

from .taxonomy import BlockType
from .value_objects import PageStats

# Legacy F11 cue
_QUESTION_STEM_RE = re.compile(r"^\s*שאלה[\s ]+[\d]")

# F52 cues
_INSTRUCTION_PREFIXES: tuple[str, ...] = ("הוראות", "קרא בעיון", "שים לב")
_DATUM_PREFIXES: tuple[str, ...] = ("נתונים",)
_LETTER_CHOICE_RE = re.compile(r"^[א-ד]\.$")  # א./ב./ג./ד.

_HEADING_HEIGHT_RATIO = 1.5
_LOW_CONFIDENCE_THRESHOLD = 0.6
_SHORT_BLOCK_WORD_COUNT = 2  # blocks ≤ 2 words and no cue → mixed


def classify_block(
    words: list[OCRWord],
    page_stats: PageStats,
) -> tuple[BlockType, float]:
    """Return ``(BlockType, confidence)`` for the given block words.

    Walks a priority-ordered cue table; first match wins. Fallback
    is ``("mixed", 0.4)`` for short unclassifiable blocks (post-F52)
    or ``("paragraph", 0.5)`` for normal-length blocks with no cue
    match (legacy F11 contract).
    """
    cues = _cue_table(words, page_stats)
    for predicate, kind, conf in cues:
        if predicate:
            return (kind, conf)
    return _fallback(words)


def _cue_table(
    words: list[OCRWord], page_stats: PageStats
) -> list[tuple[bool, BlockType, float]]:
    """Priority-ordered cue dispatch — first True predicate wins."""
    return [
        (not words,                          "answer_blank",         0.85),
        (_is_instruction(words),             "instruction",          0.85),
        (_is_datum(words),                   "datum",                0.80),
        (_is_multi_choice(words),            "multi_choice_options", 0.85),
        (_is_question_stem(words),           "question_stem",        0.90),
        (_is_heading(words, page_stats),     "heading",              0.70),
    ]


def _fallback(words: list[OCRWord]) -> tuple[BlockType, float]:
    """Per Q2: short ambiguous blocks → mixed; longer plain text → paragraph."""
    if len(words) <= _SHORT_BLOCK_WORD_COUNT:
        return ("mixed", 0.4)
    return ("paragraph", 0.5)


def _leading_text(words: list[OCRWord], n: int = 4) -> str:
    return " ".join(w.text for w in words[:n])


def _is_instruction(words: list[OCRWord]) -> bool:
    leading = _leading_text(words, 3)
    return any(leading.startswith(p) for p in _INSTRUCTION_PREFIXES)


def _is_datum(words: list[OCRWord]) -> bool:
    leading = _leading_text(words, 1)
    return any(leading.startswith(p) for p in _DATUM_PREFIXES)


def _is_multi_choice(words: list[OCRWord]) -> bool:
    """≥ 3 distinct Hebrew letter-choice prefixes (א./ב./ג./ד.) in the block."""
    seen = {w.text for w in words if _LETTER_CHOICE_RE.match(w.text)}
    return len(seen) >= 3


def _is_question_stem(words: list[OCRWord]) -> bool:
    leading = _leading_text(words, 3)
    return bool(_QUESTION_STEM_RE.match(leading))


def _is_heading(words: list[OCRWord], stats: PageStats) -> bool:
    if not words or stats.median_word_height <= 0:
        return False
    avg_height = sum(w.bbox[3] - w.bbox[1] for w in words) / len(words)
    return avg_height >= stats.median_word_height * _HEADING_HEIGHT_RATIO


def is_low_confidence(confidence: float) -> bool:
    return confidence < _LOW_CONFIDENCE_THRESHOLD
