# N02/F52 T-04 — transformations[] provenance entry for classifier decisions.
#
# Spec: N02/F52 DE-04. AC: F52-S04/AC-01.
# Every confident non-fallback pick emits one provenance entry with
# kind/from/to/confidence/adr_row. Below-threshold and fallback picks: no entry.

import pytest

from tirvi.blocks.aggregation import _build_classification_provenance


_CONFIDENT_KINDS = [
    "instruction",
    "question_stem",
    "datum",
    "answer_blank",
    "multi_choice_options",
    "heading",
]
_CONFIDENT = 0.85
_BELOW_THRESHOLD = 0.5
_AT_THRESHOLD = 0.6


class TestProvenanceShape:
    @pytest.mark.parametrize("kind", _CONFIDENT_KINDS)
    def test_confident_pick_emits_one_entry(self, kind):
        entries = _build_classification_provenance(kind, _CONFIDENT)
        assert len(entries) == 1

    @pytest.mark.parametrize("kind", _CONFIDENT_KINDS)
    def test_provenance_entry_has_from_field(self, kind):
        # F52 DE-04: 'from' field carries the heuristic signature
        entry = _build_classification_provenance(kind, _CONFIDENT)[0]
        assert "from" in entry
        assert isinstance(entry["from"], str)
        assert len(entry["from"]) > 0

    @pytest.mark.parametrize("kind", _CONFIDENT_KINDS)
    def test_provenance_entry_has_to_field(self, kind):
        entry = _build_classification_provenance(kind, _CONFIDENT)[0]
        assert entry["to"] == kind

    @pytest.mark.parametrize("kind", _CONFIDENT_KINDS)
    def test_provenance_entry_has_adr_row(self, kind):
        entry = _build_classification_provenance(kind, _CONFIDENT)[0]
        assert entry["adr_row"] == "ADR-041 #20"

    @pytest.mark.parametrize("kind", _CONFIDENT_KINDS)
    def test_provenance_entry_has_confidence(self, kind):
        entry = _build_classification_provenance(kind, _CONFIDENT)[0]
        assert entry["confidence"] == _CONFIDENT


class TestProvenanceFallback:
    def test_below_threshold_emits_no_entry(self):
        entries = _build_classification_provenance("instruction", _BELOW_THRESHOLD)
        assert entries == ()

    def test_paragraph_fallback_emits_no_entry(self):
        entries = _build_classification_provenance("paragraph", _CONFIDENT)
        assert entries == ()

    def test_mixed_fallback_emits_no_entry(self):
        entries = _build_classification_provenance("mixed", _CONFIDENT)
        assert entries == ()

    def test_at_threshold_emits_entry(self):
        entries = _build_classification_provenance("instruction", _AT_THRESHOLD)
        assert len(entries) == 1
