#!/usr/bin/env python3
"""load-ontology.py — Extract tirvi YAML ontology and load into FalkorDB graph.

Reads the four ontology files and all per-feature traceability.yaml files,
maps each entity to the correct ACM schema type, and upserts nodes + edges
into the FalkorDB `tirvi` graph.

Source files:
  ontology/business-domains.yaml      -> BoundedContext, Aggregate, Entity, Epic, Capability
  ontology/dependencies.yaml          -> DEPENDS_ON edges between features
  ontology/testing.yaml               -> TestPlan nodes
  .workitems/**/traceability.yaml     -> Feature, UserStory, AcceptanceCriterion,
                                         Milestone, Spec, ADRNode + all acm_edges

Run from the ACM project checkout:
  ACM_GRAPH_NAME=tirvi ACM_BACKEND=falkordb \\
    uv run python3 /path/to/tirvi/scripts/load-ontology.py --root /path/to/tirvi
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("load-ontology")

# ---------------------------------------------------------------------------
# Edge-type mapping — tirvi YAML string → ACM EdgeType value
# ---------------------------------------------------------------------------
_EDGE_MAP: dict[str, str] = {
    "CONTAINS": "CONTAINS",
    "BELONGS_TO": "DEPENDS_ON",   # schema allows BELONGS_TO only for SkillNode→TopicNode
    "TRACED_TO": "TRACED_TO",
    "HAS_CRITERION": "HAS_CRITERION",
    "VERIFIED_BY": "VERIFIED_BY",
    "IMPLEMENTED_BY": "IMPLEMENTED_BY",
    "INFLUENCED_BY": "DEPENDS_ON",
    "EXPLAINS": "TRACED_TO",
    "REALIZED_BY": "REALIZED_BY",
    "DECOMPOSED_INTO": "DECOMPOSED_INTO",
    "FULFILLED_BY": "FULFILLED_BY",
    "DEPENDS_ON": "DEPENDS_ON",
    "TRIGGERS": "DEPENDS_ON",     # Feature not in TRIGGERS allowed src
    "requires": "DEPENDS_ON",
    "triggers": "DEPENDS_ON",
    "enables": "DEPENDS_ON",
    "informed_by": "DEPENDS_ON",
    "informs": "DEPENDS_ON",
    "gates": "DEPENDS_ON",
    "produces": "DEPENDS_ON",
    "consumes": "DEPENDS_ON",
    "shares_model_with": "DEPENDS_ON",
    "shared_state": "DEPENDS_ON",
    "regulatory": "DEPENDS_ON",
}


def _edge_type(raw: str) -> str:
    return _EDGE_MAP.get(raw, "DEPENDS_ON")


# ---------------------------------------------------------------------------
# Node factory — map tirvi ID prefix → ACM schema class + layer
# ---------------------------------------------------------------------------
def _make_node(backend_module, schema, node_id: str, name: str, description: str = ""):
    """Create the correct ACM GraphNode subclass from the node_id prefix."""
    prefix = node_id.split(":", maxsplit=1)[0] if ":" in node_id else ""
    desc = description or name

    dispatch = {
        "feature":   (schema.Feature,              schema.Layer.FEATURES),
        "bc":        (schema.BoundedContext,        schema.Layer.DESIGN),
        "aggregate": (schema.Aggregate,             schema.Layer.DESIGN),
        "spec":      (schema.Spec,                  schema.Layer.FEATURES),
        "story":     (schema.UserStory,             schema.Layer.REQUIREMENTS),
        "criterion": (schema.AcceptanceCriterion,   schema.Layer.REQUIREMENTS),
        "task":      (schema.Milestone,             schema.Layer.FEATURES),
        "diagram":   (schema.GraphNode,             schema.Layer.DESIGN),
        "adr":       (schema.ADRNode,               schema.Layer.FEATURES),
        "phase":     (schema.Phase,                 schema.Layer.FEATURES),
        "domain":    (schema.Phase,                 schema.Layer.FEATURES),
        "subdomain": (schema.Capability,            schema.Layer.FEATURES),
        "epic":      (schema.Epic,                  schema.Layer.FEATURES),
        "persona":   (schema.Entity,                schema.Layer.DESIGN),
        "bo":        (schema.Aggregate,             schema.Layer.DESIGN),
        "testplan":  (schema.TestPlan,              schema.Layer.FEATURES),
        "dep":       (schema.GraphNode,             schema.Layer.DESIGN),
    }
    cls, layer = dispatch.get(prefix, (schema.GraphNode, schema.Layer.DESIGN))
    return cls(id=node_id, name=name, description=desc, layer=layer)


def _make_edge(schema, src: str, dst: str, raw_type: str) -> schema.GraphEdge:
    return schema.GraphEdge(
        source_id=src,
        target_id=dst,
        edge_type=schema.EdgeType(_edge_type(raw_type)),
    )


# ---------------------------------------------------------------------------
# business-domains.yaml
# ---------------------------------------------------------------------------
def _bc_id(bc_name: str) -> str:
    return f"bc:{bc_name}"


def _load_business_domains(path: Path, schema) -> tuple[list, list]:
    nodes, edges = [], []
    data = yaml.safe_load(path.read_text())

    for domain in data.get("domains", []):
        dom_id = f"domain:tirvi/{domain['id'].lower()}"
        dom_node = schema.Phase(
            id=dom_id,
            name=domain["name"],
            description=f"Domain {domain['id']}: {domain['name']}",
            layer=schema.Layer.FEATURES,
        )
        nodes.append(dom_node)

        for sd in domain.get("subdomains", []):
            sd_id = f"subdomain:tirvi/{sd['id'].lower()}"
            sd_node = schema.Capability(
                id=sd_id,
                name=sd["name"],
                description=f"Subdomain {sd['id']} ({sd.get('type', '')}): {sd['name']}",
                layer=schema.Layer.FEATURES,
                domain=domain["name"],
            )
            nodes.append(sd_node)
            edges.append(_make_edge(schema, dom_id, sd_id, "CONTAINS"))

            for bc in sd.get("bounded_contexts", []):
                bc_id = _bc_id(bc["name"])
                bc_node = schema.BoundedContext(
                    id=bc_id,
                    name=bc["name"],
                    description=f"Bounded context {bc['id']}: {bc['name']}",
                    layer=schema.Layer.DESIGN,
                )
                nodes.append(bc_node)
                edges.append(_make_edge(schema, sd_id, bc_id, "CONTAINS"))

    for persona in data.get("personas", []):
        p_id = f"persona:tirvi/{persona['id'].lower()}"
        p_node = schema.Entity(
            id=p_id,
            name=persona["name"],
            description=f"{persona['name']} — {persona.get('role', '')}",
            layer=schema.Layer.DESIGN,
        )
        nodes.append(p_node)

    for bo in data.get("business_objects", []):
        bo_id = f"bo:tirvi/{bo['id'].lower()}"
        bo_type = bo.get("type", "entity")
        if bo_type == "aggregate_root":
            cls = schema.Aggregate
        elif bo_type == "domain_event":
            cls = schema.DomainEvent
        else:
            cls = schema.Entity
        bo_node = cls(
            id=bo_id,
            name=bo["name"],
            description=bo.get("description", bo["name"]),
            layer=schema.Layer.DESIGN,
        )
        nodes.append(bo_node)
        if bc_name := bo.get("owned_by_context"):
            edges.append(_make_edge(schema, _bc_id(bc_name), bo_id, "OWNS"))

    for epic in data.get("epics", []):
        ep_id = f"epic:tirvi/{epic['id'].lower()}"
        ep_node = schema.Epic(
            id=ep_id,
            name=epic["name"],
            description=epic.get("description", epic["name"]),
            layer=schema.Layer.FEATURES,
        )
        nodes.append(ep_node)
        if bc_name := epic.get("bounded_context"):
            edges.append(_make_edge(schema, ep_id, _bc_id(bc_name), "TRACED_TO"))

    return nodes, edges


# ---------------------------------------------------------------------------
# dependencies.yaml
# ---------------------------------------------------------------------------
def _feature_id_from_dep(entry: dict) -> str:
    """Convert dependency entry (skill E-format or plan F-format) to ACM feature: id."""
    raw_id = entry.get("id", "")
    name = entry.get("name", raw_id)
    # Normalise E##-F## → feature:E##-F## (stable slug from yaml id field)
    slug = raw_id.lower().replace("/", "-").replace(" ", "-")
    return f"feature:{slug}" if slug else f"feature:{name.lower().replace(' ', '-')}"


def _load_dependencies(path: Path, schema) -> tuple[list, list]:
    nodes, edges = [], []
    data = yaml.safe_load(path.read_text())

    for dep in data.get("dependencies", []):
        src = _feature_id_from_dep(dep.get("source", {}))
        dst = _feature_id_from_dep(dep.get("target", {}))
        rel = dep.get("relationship", "requires")
        dep_id = f"dep:tirvi/{dep['id'].lower()}"

        # Stub the feature nodes if they don't yet have a plan-format entry
        src_name = dep.get("source", {}).get("name", src)
        dst_name = dep.get("target", {}).get("name", dst)
        nodes.append(schema.Feature(
            id=src,
            name=src_name,
            description=src_name,
            layer=schema.Layer.FEATURES,
        ))
        nodes.append(schema.Feature(
            id=dst,
            name=dst_name,
            description=dst_name,
            layer=schema.Layer.FEATURES,
        ))

        # Dependency metadata node
        dep_node = schema.GraphNode(
            id=dep_id,
            name=dep["id"],
            description=(
                f"{dep.get('relationship','requires').upper()} — "
                f"{dep.get('rationale', '')} "
                f"[risk: {dep.get('risk_if_broken', '')}]"
            ),
            layer=schema.Layer.DESIGN,
        )
        nodes.append(dep_node)
        edges.append(_make_edge(schema, src, dst, rel))
        edges.append(_make_edge(schema, src, dep_id, "TRACED_TO"))

    return nodes, edges


# ---------------------------------------------------------------------------
# testing.yaml
# ---------------------------------------------------------------------------
def _feature_id_from_test_entry(feat_id: str) -> str:
    slug = feat_id.lower().replace("/", "-")
    return f"feature:{slug}"


def _load_testing(path: Path, schema) -> tuple[list, list]:
    nodes, edges = [], []
    data = yaml.safe_load(path.read_text())

    for entry in data.get("test_ranges", []):
        feat_id = entry.get("feature_id", "")
        ft = entry.get("ft", [])
        bt = entry.get("bt", [])
        tp_id = f"testplan:tirvi/{feat_id.lower()}"
        ft_range = f"{ft[0]}–{ft[-1]}" if len(ft) >= 2 else (ft[0] if ft else "")
        bt_range = f"{bt[0]}–{bt[-1]}" if len(bt) >= 2 else (bt[0] if bt else "")
        tp_node = schema.TestPlan(
            id=tp_id,
            name=f"TestPlan {feat_id}",
            description=f"Functional: {ft_range}  Behavioural: {bt_range}",
            layer=schema.Layer.FEATURES,
            feature_id=_feature_id_from_test_entry(feat_id),
        )
        nodes.append(tp_node)
        feat_node_id = _feature_id_from_test_entry(feat_id)
        edges.append(_make_edge(schema, feat_node_id, tp_id, "TRACED_TO"))

    return nodes, edges


# ---------------------------------------------------------------------------
# traceability.yaml (per-feature)
# ---------------------------------------------------------------------------
def _flat_node_ids(acm_nodes: dict) -> list[str]:
    """Extract all node ID strings from acm_nodes regardless of section."""
    ids = []
    for key, val in acm_nodes.items():
        if isinstance(val, str):
            ids.append(val)
        elif isinstance(val, list):
            ids.extend(v for v in val if isinstance(v, str))
    return ids


def _node_name(node_id: str) -> str:
    """Derive a human-readable name from a namespaced ACM node ID."""
    parts = node_id.split(":", 1)
    return parts[-1] if len(parts) > 1 else node_id


def _load_traceability(path: Path, schema) -> tuple[list, list]:
    nodes, edges = [], []
    data = yaml.safe_load(path.read_text())

    acm_nodes = data.get("acm_nodes", {})
    acm_edges = data.get("acm_edges", [])

    for node_id in _flat_node_ids(acm_nodes):
        name = _node_name(node_id)
        node = _make_node(None, schema, node_id, name)
        nodes.append(node)

    for edge_def in acm_edges:
        src = edge_def.get("from", "")
        dst = edge_def.get("to", "")
        raw_type = edge_def.get("type", "DEPENDS_ON")
        if src and dst:
            edges.append(_make_edge(schema, src, dst, raw_type))

    return nodes, edges


# ---------------------------------------------------------------------------
# Bridge step 1: Feature → markdown doc nodes (workitem + biz-corpus)
# ---------------------------------------------------------------------------
def _feature_name_slug(feature_id: str) -> str:
    """Strip prefix and leading F##- to get the bare name slug.

    'feature:F08-tesseract-adapter'  →  'tesseract-adapter'
    'feature:F01-docker-compose'     →  'docker-compose'
    """
    bare = feature_id.split(":", 1)[-1]          # F08-tesseract-adapter
    parts = bare.split("-", 1)
    return parts[1] if len(parts) > 1 else bare   # tesseract-adapter


def _link_feature_to_docs(
    feature_id: str,
    name_slug: str,
    feature_dir: Path,
    root: Path,
    schema,
    backend,
) -> int:
    """Add TRACED_TO edges from a Feature node to its markdown doc nodes.

    Two sources:
    - Workitem folder (*.md files in feature_dir)
    - Biz-corpus folder (docs/business-design/epics/**/*{name_slug}*.md)
    """
    added = 0
    candidates: list[Path] = list(feature_dir.glob("*.md"))

    epics_dir = root / "docs" / "business-design" / "epics"
    if epics_dir.exists() and name_slug:
        candidates.extend(epics_dir.rglob(f"*{name_slug}*.md"))

    for md_file in candidates:
        rel = str(md_file.relative_to(root))
        doc_id = f"doc:{rel}"
        try:
            if backend.get_node(doc_id):
                backend.add_edge(schema.GraphEdge(
                    source_id=feature_id,
                    target_id=doc_id,
                    edge_type=schema.EdgeType.TRACED_TO,
                ))
                added += 1
        except Exception:
            pass

    return added


def _build_workitem_bridges(root: Path, schema, backend) -> int:
    """Link every YAML Feature node to its markdown doc nodes."""
    workitems = root / ".workitems"
    added = 0
    for tf in workitems.rglob("traceability.yaml"):
        try:
            data = yaml.safe_load(tf.read_text())
        except Exception:
            continue
        feature_id = (data.get("acm_nodes") or {}).get("feature", "")
        if not feature_id:
            continue
        name_slug = _feature_name_slug(feature_id)
        added += _link_feature_to_docs(
            feature_id, name_slug, tf.parent, root, schema, backend
        )
    log.info("Workitem bridge edges added: %d", added)
    return added


# ---------------------------------------------------------------------------
# Bridge step 2: E-format dep stubs → canonical F-format features
# ---------------------------------------------------------------------------
def _build_crosswalk_bridges(root: Path, schema, backend) -> int:
    """Add TRACED_TO edges from E-format dep stubs to F-format plan features.

    Uses plan_md_cross_walk from business-domains.yaml. Links each E-format
    skill feature to all plan features in the same epic group.
    """
    biz_path = root / "ontology" / "business-domains.yaml"
    if not biz_path.exists():
        return 0

    data = yaml.safe_load(biz_path.read_text())
    added = 0
    for row in data.get("plan_md_cross_walk", []):
        plan_feats = [f"feature:{pf.lower()}" for pf in row.get("plan_features", [])]
        skill_feats = [f"feature:{sf.lower()}" for sf in row.get("skill_features", [])]
        for e_id in skill_feats:
            for f_id in plan_feats:
                try:
                    backend.add_edge(schema.GraphEdge(
                        source_id=e_id,
                        target_id=f_id,
                        edge_type=schema.EdgeType.TRACED_TO,
                    ))
                    added += 1
                except Exception:
                    pass
    log.info("Crosswalk bridge edges added: %d", added)
    return added


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Load tirvi YAML ontology into FalkorDB.")
    p.add_argument("--root", required=True, help="Path to the tirvi project root")
    p.add_argument("--dry-run", action="store_true", help="Parse only; do not write to graph")
    return p.parse_args()


def _collect_all(root: Path, schema) -> tuple[list, list]:
    all_nodes: list = []
    all_edges: list = []

    ontology = root / "ontology"
    for loader, filename in [
        (_load_business_domains, "business-domains.yaml"),
        (_load_dependencies, "dependencies.yaml"),
        (_load_testing, "testing.yaml"),
    ]:
        fp = ontology / filename
        if fp.exists():
            n, e = loader(fp, schema)
            log.info("  %s → %d nodes, %d edges", filename, len(n), len(e))
            all_nodes.extend(n)
            all_edges.extend(e)
        else:
            log.warning("  %s not found — skipping", fp)

    workitems = root / ".workitems"
    trace_files = list(workitems.rglob("traceability.yaml"))
    log.info("traceability.yaml files found: %d", len(trace_files))
    for tf in trace_files:
        n, e = _load_traceability(tf, schema)
        all_nodes.extend(n)
        all_edges.extend(e)

    return all_nodes, all_edges


def main() -> None:
    args = _parse_args()
    root = Path(args.root).resolve()

    # Late imports so the script can be discovered without ACM installed
    try:
        from agent_context_manager import schema
        from agent_context_manager.config import ProjectConfig
        from agent_context_manager.db.factory import create_backend
    except ImportError as exc:
        log.error("Run this script from the ACM project checkout: %s", exc)
        sys.exit(1)

    log.info("Collecting nodes + edges from %s …", root)
    all_nodes, all_edges = _collect_all(root, schema)

    # Deduplicate nodes by ID (last write wins — upsert semantics)
    seen: dict[str, object] = {}
    for node in all_nodes:
        seen[node.id] = node
    unique_nodes = list(seen.values())

    log.info("Total unique nodes: %d  edges: %d", len(unique_nodes), len(all_edges))

    if args.dry_run:
        log.info("--dry-run: skipping graph write")
        return

    config = ProjectConfig.from_env(project_name="tirvi")
    backend = create_backend(config)

    upserted, failed_nodes = 0, 0
    for node in unique_nodes:
        try:
            backend.upsert_node(node)
            upserted += 1
        except Exception as exc:
            log.debug("Node upsert failed %s: %s", node.id, exc)
            failed_nodes += 1

    added, failed_edges = 0, 0
    for edge in all_edges:
        try:
            backend.add_edge(edge)
            added += 1
        except Exception as exc:
            log.debug("Edge add failed %s→%s: %s", edge.source_id, edge.target_id, exc)
            failed_edges += 1

    log.info(
        "Done — upserted %d nodes (%d failed), added %d edges (%d failed)",
        upserted, failed_nodes, added, failed_edges,
    )

    log.info("Running bridge passes …")
    _build_workitem_bridges(root, schema, backend)
    _build_crosswalk_bridges(root, schema, backend)


if __name__ == "__main__":
    main()
