"""F21 — Homograph value objects.

Spec: N02/F21 DE-01. AC: US-01/AC-01.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HomographEntry:
    """One homograph override entry.

    Invariants:
      - INV-HOM-ENTRY-001 (DE-01): ``surface_form`` is the undecorated text
      - INV-HOM-ENTRY-002 (DE-01): ``vocalized_form`` is the preferred nikud
      - INV-HOM-ENTRY-003 (DE-01): ``pos_filter`` optionally constrains the
        match to one POS (POC loader skips entries with pos_filter set).
    """

    surface_form: str
    vocalized_form: str
    pos_filter: str | None = None
