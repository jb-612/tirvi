"""F08 T-03 — RTL multi-column reorder.

Spec: N01/F08 DE-03. AC: US-01/AC-01. FT-anchors: FT-057, FT-062.

Hebrew reading order: rightmost column first; within a column, top to
bottom; within a row, right-to-left. This module clusters Tesseract word
boxes into columns by x-center gap and emits them in that reading order.

INV-TESS-003 (BT-040): RTL multi-column page reorder via x-center clustering.
"""

from __future__ import annotations

from tirvi.results import OCRWord


def reorder_rtl_columns(words: list[OCRWord]) -> list[OCRWord]:
    """Reorder ``words`` into Hebrew reading order (right-to-left, multi-col).

    Strategy:

    1. Cluster words into columns by gap in x-center (gap threshold derived
       from median word width).
    2. Sort columns by max x-center descending (rightmost first).
    3. Within each column, sort by y-center ascending, then x-center
       descending for same-row ties.
    """
    if len(words) <= 1:
        return list(words)
    columns = _cluster_columns(words)
    columns.sort(key=lambda col: -max(_x_center(w) for w in col))
    result: list[OCRWord] = []
    for col in columns:
        col.sort(key=lambda w: (_y_center(w), -_x_center(w)))
        result.extend(col)
    return result


def _cluster_columns(words: list[OCRWord]) -> list[list[OCRWord]]:
    sorted_words = sorted(words, key=_x_center)
    threshold = 1.5 * max(_median_word_width(words), 1)
    columns: list[list[OCRWord]] = [[sorted_words[0]]]
    prev_x = _x_center(sorted_words[0])
    for word in sorted_words[1:]:
        cur_x = _x_center(word)
        if cur_x - prev_x > threshold:
            columns.append([word])
        else:
            columns[-1].append(word)
        prev_x = cur_x
    return columns


def _median_word_width(words: list[OCRWord]) -> float:
    widths = sorted(w.bbox[2] - w.bbox[0] for w in words)
    return float(widths[len(widths) // 2])


def _x_center(word: OCRWord) -> float:
    return (word.bbox[0] + word.bbox[2]) / 2.0


def _y_center(word: OCRWord) -> float:
    return (word.bbox[1] + word.bbox[3]) / 2.0
