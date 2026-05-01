"""F08 T-03 — RTL column reorder.

Spec: N01/F08 DE-03. AC: US-01/AC-01. FT-anchors: FT-057, FT-062.
"""

from __future__ import annotations

from tirvi.adapters.tesseract.layout import reorder_rtl_columns
from tirvi.results import OCRWord


def _w(text: str, x0: int, y0: int, x1: int, y1: int) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), confidence=1.0)


class TestRTLColumnReorder:
    def test_us_01_ac_01_ft_062_two_lines_each_with_two_words(self) -> None:
        """Line-major RTL reading: each line's words emit right-to-left,
        then move to the next line. Two-column column-major reading for
        true multi-column documents is deferred to MVP (issue #17)."""
        right_top = _w("ימין-עליון", 750, 10, 850, 50)
        right_bot = _w("ימין-תחתון", 750, 100, 850, 140)
        left_top = _w("שמאל-עליון", 150, 10, 250, 50)
        left_bot = _w("שמאל-תחתון", 150, 100, 250, 140)

        scrambled = [left_top, right_bot, right_top, left_bot]
        ordered = reorder_rtl_columns(scrambled)

        # Line 1 (y≈30): right_top, left_top read right-to-left.
        # Line 2 (y≈120): right_bot, left_bot read right-to-left.
        assert ordered == [right_top, left_top, right_bot, left_bot]

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

    def test_us_01_ac_01_dense_single_column_three_lines(self) -> None:
        """Issue #17 — realistic Hebrew single-column page.

        Three lines, four words each, words ~80 px wide with ~20 px spaces.
        Threshold (1.5 × median width = 120 px) is exceeded by the natural
        word gap on each line, which previously caused mid-line splits.
        """
        # Line 1 (y≈30): 4 words right→left at x_centers 950, 800, 650, 500
        l1_w1 = _w("הבחינה", 910, 10, 990, 50)      # x-center 950
        l1_w2 = _w("בחשבונאות", 760, 10, 840, 50)   # x-center 800
        l1_w3 = _w("מועד", 610, 10, 690, 50)        # x-center 650
        l1_w4 = _w("א'", 460, 10, 540, 50)          # x-center 500

        # Line 2 (y≈80): 4 words right→left at x_centers 950, 800, 650, 500
        l2_w1 = _w("שנת", 910, 60, 990, 100)
        l2_w2 = _w("תשפ\"ה", 760, 60, 840, 100)
        l2_w3 = _w("מצב", 610, 60, 690, 100)
        l2_w4 = _w("הבחינה", 460, 60, 540, 100)

        # Line 3 (y≈130): 4 words right→left
        l3_w1 = _w("בחר", 910, 110, 990, 150)
        l3_w2 = _w("את", 760, 110, 840, 150)
        l3_w3 = _w("התשובה", 610, 110, 690, 150)
        l3_w4 = _w("הנכונה", 460, 110, 540, 150)

        scrambled = [
            l3_w2, l1_w4, l2_w1, l3_w1, l1_w1, l2_w3,
            l3_w4, l1_w3, l2_w4, l1_w2, l2_w2, l3_w3,
        ]

        ordered = reorder_rtl_columns(scrambled)

        expected = [
            l1_w1, l1_w2, l1_w3, l1_w4,  # Line 1 right→left
            l2_w1, l2_w2, l2_w3, l2_w4,  # Line 2 right→left
            l3_w1, l3_w2, l3_w3, l3_w4,  # Line 3 right→left
        ]
        assert ordered == expected, (
            f"Expected line-by-line right-to-left order, got "
            f"{[w.text for w in ordered]}"
        )

    def test_us_01_ac_01_words_with_jittery_y_centers_same_line(self) -> None:
        """Words on the same printed line have slightly different y-centers
        due to ascenders / descenders. They must still group as one line."""
        # Three words on "one line" with y-centers 30, 32, 28 (within ~half height)
        right = _w("right", 800, 10, 880, 50)   # y-center 30
        mid = _w("mid", 600, 12, 680, 52)       # y-center 32
        left = _w("left", 400, 8, 480, 48)      # y-center 28

        ordered = reorder_rtl_columns([mid, left, right])

        assert ordered == [right, mid, left]
