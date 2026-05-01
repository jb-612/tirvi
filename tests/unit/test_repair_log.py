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
    return OCRWord(text=text, bbox=(0, 0, 50, 30), confidence=1.0)


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


class TestRepairLogEmitter:
    """T-06 — DE-06: repair-log emitter with deterministic ordering.

    Each rule application appends a ``RepairLogEntry``. The composed log
    is sorted deterministically by ``(rule_id, position)`` so that two
    runs over identical input produce byte-identical logs (BT-066).
    """

    def test_emits_entries_for_each_rule_application(self) -> None:
        from tirvi.normalize.compose import normalize

        # Two adjacent words across a line break (rejoin) plus a stray
        # comma alone on its own line (drop).
        words = [
            OCRWord(text="hyph", bbox=(0, 0, 50, 20), confidence=0.9),
            OCRWord(text="enword", bbox=(0, 40, 50, 60), confidence=0.9),
            OCRWord(text=",", bbox=(0, 100, 10, 120), confidence=0.2),
        ]
        result = normalize(words)
        rule_ids = [e.rule_id for e in result.repair_log]
        assert "line_break_rejoin" in rule_ids
        assert "stray_punct_drop" in rule_ids

    def test_repair_log_is_sorted_deterministically(self) -> None:
        from tirvi.normalize.compose import normalize

        words = [
            OCRWord(text="alpha", bbox=(0, 0, 50, 20), confidence=0.9),
            OCRWord(text=",", bbox=(0, 40, 10, 60), confidence=0.2),
            OCRWord(text="beta", bbox=(0, 80, 50, 100), confidence=0.9),
            OCRWord(text="gamma", bbox=(0, 120, 50, 140), confidence=0.9),
        ]
        result = normalize(words)
        keys = [(e.rule_id, e.position) for e in result.repair_log]
        assert keys == sorted(keys)

    def test_position_is_char_offset_in_output_text(self) -> None:
        from tirvi.normalize.compose import normalize

        words = [
            OCRWord(text="hyph", bbox=(0, 0, 50, 20), confidence=0.9),
            OCRWord(text="enword", bbox=(0, 40, 50, 60), confidence=0.9),
        ]
        result = normalize(words)
        rejoin_entries = [
            e for e in result.repair_log if e.rule_id == "line_break_rejoin"
        ]
        assert len(rejoin_entries) == 1
        entry = rejoin_entries[0]
        # position must point into result.text such that result.text starts
        # with entry.after at that offset.
        assert result.text[entry.position : entry.position + len(entry.after)] == entry.after
