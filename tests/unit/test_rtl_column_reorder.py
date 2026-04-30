"""F08 T-03 — RTL column reorder.

Spec: N01/F08 DE-03. AC: US-01/AC-01. FT-anchors: FT-057, FT-062.
"""

from __future__ import annotations

from tirvi.adapters.tesseract.layout import reorder_rtl_columns
from tirvi.results import OCRWord


def _w(text: str, x0: int, y0: int, x1: int, y1: int) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), conf=1.0)


class TestRTLColumnReorder:
    def test_us_01_ac_01_ft_062_clusters_words_by_x_center(self) -> None:
        # Two columns: right column words have x-center ≈ 800; left column ≈ 200
        right_top = _w("ימין-עליון", 750, 10, 850, 50)
        right_bot = _w("ימין-תחתון", 750, 100, 850, 140)
        left_top = _w("שמאל-עליון", 150, 10, 250, 50)
        left_bot = _w("שמאל-תחתון", 150, 100, 250, 140)

        # Tesseract gives them in arbitrary order
        scrambled = [left_top, right_bot, right_top, left_bot]
        ordered = reorder_rtl_columns(scrambled)

        # Right column read first; within column top to bottom
        assert ordered == [right_top, right_bot, left_top, left_bot]

    def test_us_01_ac_01_ft_062_sorts_columns_max_x_descending(self) -> None:
        # 3 columns. Rightmost (x≈900) read first, middle (x≈500), then left (x≈100).
        a = _w("a", 50, 0, 150, 30)
        b = _w("b", 450, 0, 550, 30)
        c = _w("c", 850, 0, 950, 30)

        ordered = reorder_rtl_columns([a, b, c])

        assert ordered == [c, b, a]

    def test_us_01_ac_01_ft_057_within_column_sort_y_asc_then_x_desc(self) -> None:
        # Same column (x ≈ 500), three words; same y on top row, different x.
        # Within a row Hebrew reads right-to-left → higher x first.
        top_left = _w("top-left", 460, 10, 510, 40)
        top_right = _w("top-right", 540, 10, 590, 40)
        bottom = _w("bottom", 480, 100, 570, 130)

        ordered = reorder_rtl_columns([bottom, top_left, top_right])

        assert ordered == [top_right, top_left, bottom]

    def test_empty_input_returns_empty(self) -> None:
        assert reorder_rtl_columns([]) == []

    def test_single_word_returns_singleton(self) -> None:
        only = _w("only", 100, 100, 200, 130)
        assert reorder_rtl_columns([only]) == [only]
