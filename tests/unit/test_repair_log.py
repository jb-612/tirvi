"""F14 T-05 — RepairLogEntry audit trail (POC numbering).

Spec: N02/F14 DE-04, DE-06. AC: US-01/AC-01, US-02/AC-01.
FT-anchors: FT-098. BT-anchors: BT-066.
"""

from __future__ import annotations

import pytest

from tirvi.normalize.passthrough import normalize_text
from tirvi.normalize.value_objects import RepairLogEntry
from tirvi.results import OCRWord


def _w(text: str) -> OCRWord:
    return OCRWord(text=text, bbox=(0, 0, 50, 30), conf=1.0)


class TestRepairLog:
    def test_us_01_ac_01_repair_entry_records_rule_id(self) -> None:
        entry = RepairLogEntry(
            rule_id="line_break_rejoin",
            before="hyphen-",
            after="hyphenword",
            position=12,
        )
        assert entry.rule_id == "line_break_rejoin"

    def test_us_01_ac_01_repair_entry_records_before_after(self) -> None:
        entry = RepairLogEntry(
            rule_id="stray_punct_drop",
            before=",",
            after="",
            position=3,
        )
        assert entry.before == ","
        assert entry.after == ""

    def test_us_01_ac_01_no_repairs_means_empty_log(self) -> None:
        # POC pass-through path applies no repair rules.
        result = normalize_text([_w("שלום"), _w("עולם")])
        assert result.repair_log == ()

    def test_repair_log_entry_is_frozen(self) -> None:
        from dataclasses import FrozenInstanceError

        entry = RepairLogEntry(rule_id="r", before="a", after="b", position=0)
        with pytest.raises(FrozenInstanceError):
            entry.rule_id = "other"  # type: ignore[misc]
