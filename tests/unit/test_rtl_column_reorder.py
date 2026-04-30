"""F08 T-03 — RTL column reorder.

Spec: N01/F08 DE-03. AC: US-01/AC-01. FT-anchors: FT-057, FT-062.
"""

import pytest


@pytest.mark.skip(reason="scaffold — TDD fills")
class TestRTLColumnReorder:
    def test_us_01_ac_01_ft_062_clusters_words_by_x_center(self) -> None:
        pass

    def test_us_01_ac_01_ft_062_sorts_columns_max_x_descending(self) -> None:
        # Hebrew RTL: rightmost column is read first
        pass

    def test_us_01_ac_01_ft_057_within_column_sort_y_asc_then_x_desc(self) -> None:
        pass
