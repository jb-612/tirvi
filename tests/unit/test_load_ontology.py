# scripts/load-ontology.py — characterization + new-helper tests.
#
# Covers: pure helpers (RED/GREEN baseline) and the four functions
# extracted to bring _load_business_domains + _build_crosswalk_bridges
# + main below CC 5.

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ── module loader ──────────────────────────────────────────────────────────────
_SCRIPT = Path(__file__).parent.parent.parent / "scripts" / "load-ontology.py"


def _load():
    spec = importlib.util.spec_from_file_location("load_ontology", _SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_mod = _load()


# ── existing pure helpers (characterisation — should stay GREEN) ───────────────

class TestEdgeType:
    def test_known_passthrough(self):
        assert _mod._edge_type("CONTAINS") == "CONTAINS"
        assert _mod._edge_type("TRACED_TO") == "TRACED_TO"

    def test_aliased_to_depends_on(self):
        assert _mod._edge_type("requires") == "DEPENDS_ON"
        assert _mod._edge_type("INFLUENCED_BY") == "DEPENDS_ON"

    def test_unknown_defaults_to_depends_on(self):
        assert _mod._edge_type("totally_unknown") == "DEPENDS_ON"


class TestBcId:
    def test_prefixes_correctly(self):
        assert _mod._bc_id("audio_delivery") == "bc:audio_delivery"


class TestNodeName:
    def test_strips_namespace(self):
        assert _mod._node_name("feature:my-feature") == "my-feature"

    def test_no_namespace_returns_whole(self):
        assert _mod._node_name("plainname") == "plainname"


class TestFlatNodeIds:
    def test_string_values_included(self):
        result = _mod._flat_node_ids({"feature": "feature:f01"})
        assert "feature:f01" in result

    def test_list_values_expanded(self):
        result = _mod._flat_node_ids({"stories": ["story:s1", "story:s2"]})
        assert result == ["story:s1", "story:s2"]

    def test_non_string_list_items_skipped(self):
        result = _mod._flat_node_ids({"mixed": ["story:s1", 42, None]})
        assert result == ["story:s1"]


class TestFeatureNameSlug:
    def test_strips_f_prefix(self):
        assert _mod._feature_name_slug("feature:F08-tesseract-adapter") == "tesseract-adapter"

    def test_no_dash_returns_whole_bare(self):
        assert _mod._feature_name_slug("feature:F01") == "F01"


# ── new helpers (RED until extracted from the refactored CC-heavy functions) ───

class TestBoClass:
    def test_aggregate_root(self):
        schema = MagicMock()
        assert _mod._bo_class("aggregate_root", schema) is schema.Aggregate

    def test_domain_event(self):
        schema = MagicMock()
        assert _mod._bo_class("domain_event", schema) is schema.DomainEvent

    def test_other_type_returns_entity(self):
        schema = MagicMock()
        assert _mod._bo_class("entity", schema) is schema.Entity

    def test_unknown_type_returns_entity(self):
        schema = MagicMock()
        assert _mod._bo_class("value_object", schema) is schema.Entity


class TestPlanFeatureIds:
    def test_lowercases_and_prefixes(self):
        row = {"plan_features": ["F01-db-port", "F02-schema"]}
        result = _mod._plan_feature_ids(row)
        assert result == ["feature:f01-db-port", "feature:f02-schema"]

    def test_missing_key_returns_empty(self):
        assert _mod._plan_feature_ids({}) == []


class TestSkillFeatureIds:
    def test_lowercases_and_prefixes(self):
        row = {"skill_features": ["E01-F01", "E02-F05"]}
        result = _mod._skill_feature_ids(row)
        assert result == ["feature:e01-f01", "feature:e02-f05"]

    def test_missing_key_returns_empty(self):
        assert _mod._skill_feature_ids({}) == []


class TestDedupNodes:
    def test_deduplicates_by_id_last_wins(self):
        n1 = MagicMock(); n1.id = "feature:f01"; n1.name = "first"
        n2 = MagicMock(); n2.id = "feature:f01"; n2.name = "second"
        n3 = MagicMock(); n3.id = "feature:f02"
        result = _mod._dedup_nodes([n1, n2, n3])
        assert len(result) == 2
        ids = {n.id for n in result}
        assert ids == {"feature:f01", "feature:f02"}

    def test_last_write_wins(self):
        n1 = MagicMock(); n1.id = "x"; n1.name = "first"
        n2 = MagicMock(); n2.id = "x"; n2.name = "second"
        result = _mod._dedup_nodes([n1, n2])
        assert result[0].name == "second"
