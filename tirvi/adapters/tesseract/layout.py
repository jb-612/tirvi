"""F08 T-03 — RTL line-first reorder.

Spec: N01/F08 DE-03. AC: US-01/AC-01. FT-anchors: FT-057, FT-062.

Hebrew reading order on a single-column page: top-to-bottom by line,
right-to-left within each line. POC scope is single-column (Economy.pdf
p.1); true multi-column documents that need column-major reading are
deferred to MVP because robust column-boundary detection requires a
whole-page x-center histogram. See issue #17 for the bug history.

INV-TESS-003 (BT-040): RTL line-first reorder via y-center grouping.
"""

from __future__ import annotations

from tirvi.results import OCRWord


def reorder_rtl_columns(words: list[OCRWord]) -> list[OCRWord]:
    """Reorder ``words`` into Hebrew reading order.

    1. Group words into lines by y-center bands (tolerance = half the
       median word height — robust to ascender / descender jitter).
    2. Sort lines top-to-bottom.
    3. Within each line, sort by x-center descending (right-to-left).
    """
    if len(words) <= 1:
        return list(words)
    lines = _group_into_lines(words)
    result: list[OCRWord] = []
    for line in lines:
        line.sort(key=lambda w: -_x_center(w))
        result.extend(line)
    return result


def _group_into_lines(words: list[OCRWord]) -> list[list[OCRWord]]:
    sorted_by_y = sorted(words, key=_y_center)
    tolerance = 0.5 * max(_median_word_height(words), 1)
    lines: list[list[OCRWord]] = [[sorted_by_y[0]]]
    prev_y = _y_center(sorted_by_y[0])
    for word in sorted_by_y[1:]:
        cur_y = _y_center(word)
        if cur_y - prev_y > tolerance:
            lines.append([word])
        else:
            lines[-1].append(word)
        prev_y = cur_y
    return lines


def _median_word_height(words: list[OCRWord]) -> float:
    heights = sorted(w.bbox[3] - w.bbox[1] for w in words)
    return float(heights[len(heights) // 2])


def _x_center(word: OCRWord) -> float:
    return (word.bbox[0] + word.bbox[2]) / 2.0


def _y_center(word: OCRWord) -> float:
    return (word.bbox[1] + word.bbox[3]) / 2.0
