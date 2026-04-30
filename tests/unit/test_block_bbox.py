"""F11 T-04 — block bbox aggregation + word coverage.

Spec: N01/F11 DE-05, DE-06. AC: US-01/AC-01. FT-anchors: FT-074.
"""

from __future__ import annotations

import pytest

from tirvi.blocks.aggregation import aggregate_block_bbox, build_blocks
from tirvi.blocks.value_objects import PageStats
from tirvi.results import OCRWord


def _w(text: str, x0: int, y0: int, x1: int, y1: int) -> OCRWord:
    return OCRWord(text=text, bbox=(x0, y0, x1, y1), conf=1.0)


_STATS = PageStats(median_word_height=30.0, modal_x_start=100, line_spacing=40.0)


class TestBlockBbox:
    def test_us_01_ac_01_block_bbox_is_union_of_child_words(self) -> None:
        words = [
            _w("a", 100, 50, 150, 80),
            _w("b", 160, 55, 220, 90),
        ]
        bbox = aggregate_block_bbox(words)
        assert bbox == (100, 50, 220, 90)

    def test_us_01_ac_01_every_word_in_exactly_one_block(self) -> None:
        # Three rows of words; second row gap = 270 (≫ line_spacing 40) → block break.
        words = [
            _w("h1", 100, 0, 200, 80),
            _w("p1", 100, 100, 150, 130),
            _w("p2", 160, 100, 210, 130),
            _w("p3", 100, 400, 150, 430),
        ]
        blocks = build_blocks(words, _STATS)

        seen: list[int] = []
        for blk in blocks:
            seen.extend(blk.child_word_indices)
        assert sorted(seen) == list(range(len(words)))

    def test_us_01_ac_01_block_id_format_b_n(self) -> None:
        words = [
            _w("h", 100, 0, 200, 80),
            _w("p", 100, 200, 200, 230),
        ]
        blocks = build_blocks(words, _STATS)
        assert [b.block_id for b in blocks] == ["b1", "b2"]

    def test_empty_word_list_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            aggregate_block_bbox([])
