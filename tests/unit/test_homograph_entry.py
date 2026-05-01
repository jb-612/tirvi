"""F21 T-01 — HomographEntry value object.

Spec: N02/F21 DE-01. AC: US-01/AC-01. FT: FT-158.
"""

import dataclasses

import pytest

from tirvi.homograph.value_objects import HomographEntry


def test_homograph_entry_constructs_with_required_fields():
    entry = HomographEntry(surface_form="כל", vocalized_form="כֹּל")
    assert entry.surface_form == "כל"
    assert entry.vocalized_form == "כֹּל"
    assert entry.pos_filter is None


def test_homograph_entry_accepts_pos_filter():
    entry = HomographEntry(surface_form="ספר", vocalized_form="סָפַר", pos_filter="VERB")
    assert entry.pos_filter == "VERB"


def test_homograph_entry_is_frozen():
    entry = HomographEntry(surface_form="כל", vocalized_form="כֹּל")
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.surface_form = "x"  # type: ignore[misc]
