"""F11 T-01 — per-page heuristic stats (page statistics aggregator).

Spec: N01/F11 DE-02. AC: US-01/AC-01. FT-anchors: FT-074.
"""

from __future__ import annotations

from tirvi.blocks.page_stats import compute_page_stats
from tirvi.results import OCRWord


def _w(x0: int, y0: int, x1: int, y1: int) -> OCRWord:
    return OCRWord(text="x", bbox=(x0, y0, x1, y1), conf=1.0)


class TestPageStatistics:
    def test_us_01_ac_01_median_word_height_positive(self) -> None:
        words = [
            _w(0, 0, 50, 40),       # height 40
            _w(0, 50, 50, 100),     # height 50
            _w(0, 110, 50, 170),    # height 60
        ]
        stats = compute_page_stats(words)
        assert stats.median_word_height == 50.0

    def test_us_01_ac_01_modal_x_start_in_page_frame(self) -> None:
        words = [
            _w(100, 0, 200, 40),
            _w(100, 50, 200, 100),
            _w(100, 120, 200, 170),
            _w(800, 200, 900, 240),  # outlier x-start
        ]
        stats = compute_page_stats(words)
        assert stats.modal_x_start == 100

    def test_us_01_ac_01_line_spacing_from_consecutive_words(self) -> None:
        # Three rows: y-tops 0, 100, 200 → spacing 100
        words = [
            _w(0, 0, 50, 40),
            _w(0, 100, 50, 140),
            _w(0, 200, 50, 240),
        ]
        stats = compute_page_stats(words)
        assert stats.line_spacing == 100.0
