# Ontology Schemas

Each `*.schema.yaml` file documents the structure of one ontology layer
file. They are **descriptive**, not enforced by a runtime validator
today; `scripts/validate-ontology.sh` checks file presence + YAML
parsability + node-id uniqueness, but does not yet enforce field-level
schema conformance. That gap is intentional — the schemas exist to:

1. Document expected structure for humans and skills.
2. Guide future automated validation when complexity warrants it.
3. Define node-id namespace conventions that the ACM ingest CLI
   indirectly relies on (it parses YAML by key names and node IDs).

## File-to-schema mapping

| File | Schema |
|---|---|
| `ontology/business-domains.yaml` | `schemas/business-domains.schema.yaml` |
| `ontology/technical-implementation.yaml` | `schemas/technical-implementation.schema.yaml` |
| `ontology/testing.yaml` | `schemas/testing.schema.yaml` |
| `ontology/dependencies.yaml` | `schemas/dependencies.schema.yaml` |

## Node-id namespace (canonical)

See `ontology/README.md` for the full table. Schemas reference
`graph_id_prefix` for nodes whose YAML id is a short code (e.g., `D01`)
but whose graph-id has a typed prefix (e.g., `domain:D01`).

## Future graphdb-loader semantics

The schemas are designed for future direct-load into FalkorDB via a
property-graph mapper:

- Each top-level array becomes a node-type collection.
- `id` field becomes the graph node ID (with prefix prepended where
  documented).
- `*_ref` and `*_refs` fields become outgoing edges; the edge type is
  inferred from field name (`port_ref` → `IMPLEMENTS`, `module_ref` →
  `BELONGS_TO`, `bounded_context` → `IN_CONTEXT`).
- Explicit edges live in `dependencies.yaml` — the relationship enum
  is the canonical edge-type vocabulary.

For now, ACM ingestion relies on its own parsing of YAML files in
`ACM_DOC_DIRS`. The schemas here document structure for humans; ACM
discovers nodes algorithmically.
