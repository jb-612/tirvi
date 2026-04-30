"""F11 T-01 — per-page heuristic stats.

Spec: N01/F11 DE-02. AC: US-01/AC-01. FT-anchors: FT-074.

Pure function over a flat list of :class:`tirvi.results.OCRWord`. Output is
a :class:`PageStats` consumed by the block classifier.
"""

from __future__ import annotations

from collections import Counter
from statistics import median

from tirvi.results import OCRWord

from .value_objects import PageStats


def compute_page_stats(words: list[OCRWord]) -> PageStats:
    """Compute heuristic stats over OCR word boxes."""
    return PageStats(
        median_word_height=_median_word_height(words),
        modal_x_start=_modal_x_start(words),
        line_spacing=_median_line_spacing(words),
    )


def _median_word_height(words: list[OCRWord]) -> float:
    heights = [w.bbox[3] - w.bbox[1] for w in words]
    return float(median(heights)) if heights else 0.0


def _modal_x_start(words: list[OCRWord]) -> int:
    x_starts = [w.bbox[0] for w in words]
    if not x_starts:
        return 0
    return Counter(x_starts).most_common(1)[0][0]


def _median_line_spacing(words: list[OCRWord]) -> float:
    y_tops = sorted({w.bbox[1] for w in words})
    if len(y_tops) < 2:
        return 0.0
    diffs = [y_tops[i + 1] - y_tops[i] for i in range(len(y_tops) - 1)]
    return float(median(diffs))
