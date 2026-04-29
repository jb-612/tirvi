# Project Ontology — tirvi

This folder is the **project-level graph slice**: nodes and edges that
span features, contexts, and layers. Per-feature graph slices live in
`.workitems/<N>/<F>/traceability.yaml`. Both feed the existing ACM
(Architecture Concept Model) graph database.

See `docs/ADR/ADR-013-sdlc-biz-sw-design-split.md` for the architectural
rationale.

## Layered files

| File | Layer | Owner | Lifecycle |
|---|---|---|---|
| `business-domains.yaml` | Business domain | `@biz-functional-design` | design-time |
| `technical-implementation.yaml` | Software layer | `@sw-designpipeline` | design + run-time |
| `testing.yaml` | Test layer | `@biz-functional-design` (definitions) + TDD (status) | design + run-time |
| `dependencies.yaml` | Cross-layer edges | both biz and sw skills | design-time |

## Node-id namespace

Every node has a globally-unique ID with a type-prefix. Cross-references
use these IDs verbatim — no slicing, no duplication.

| Type | Prefix | Layer | Examples |
|---|---|---|---|
| Domain | `domain:` | business | `domain:D01` |
| Bounded context | `bc:` | business | `bc:hebrew_text` |
| Persona | `persona:` | business | `persona:P01` |
| Business object | `bo:` | business | `bo:Document`, `bo:Page` |
| Collaboration object | `co:` | business | `co:CO01` (OCR Engine) |
| Feature | `feature:` | features | `feature:N00-F01` |
| Spec / design element | `spec:` | design | `spec:N00-F01/DE-01` |
| User story | `story:` | requirements | `story:N00-F01/US-01` |
| Acceptance criterion | `criterion:` | requirements | `criterion:N00-F01/US-01/AC-01` |
| Task | `task:` | tasks | `task:N00-F01/T-01` |
| Module | `module:` | software | `module:internal/repo` |
| Service | `service:` | software | `service:api`, `service:worker` |
| Port | `port:` | software | `port:Storage`, `port:OCR` |
| Adapter | `adapter:` | software | `adapter:GCSStorage` |
| Class | `class:` | software | `class:DocumentRepository` |
| Function | `fn:` | software | `fn:NewServer` |
| ADR | `adr:` | software | `adr:013` |
| Functional test | `ft:` | testing | `ft:N00-F01/01` |
| Behavioural test | `bt:` | testing | `bt:N00-F01/01` |

## Edge types

Edges live in `dependencies.yaml`. Existing types from the workitem
template are preserved; new types added by this refactor:

| Edge | Source layer | Target layer | Meaning |
|---|---|---|---|
| `TRACED_TO` | any | any | hierarchical / lineage |
| `IMPLEMENTED_BY` | spec | task | spec realized by a task |
| `HAS_CRITERION` | story | criterion | story owns its ACs |
| `CONTAINS` | feature | spec/story/etc | feature scope |
| `VERIFIED_BY` | spec / criterion | test | testable assertion |
| `REALIZES` (NEW) | software | business | sw layer satisfies biz layer |
| `TESTED_BY` (NEW) | software | testing | code layer covered by tests |
| `DEPENDS_ON` | any | any | runtime / build-time dependency |
| `REPLACES` | adr | adr / decision | supersession |

## ACM ingestion

This folder + `.workitems/<N>/<F>/traceability.yaml` files are loaded
into FalkorDB via the existing ACM CLI. **The ingestion is run from
your ACM project checkout**, with `--root` pointing at tirvi as the
target codebase. The `acm` CLI is not installed in tirvi's uv env (and
should not be) — it lives with the ACM project.

From your ACM checkout (e.g., `~/code/acm-mcp/`):

```bash
ACM_GRAPH_NAME=tirvi \
ACM_DOC_DIRS="docs,ontology,.workitems" \
ACM_SOURCE_DIRS="cmd,pkg,internal,flutter_app/lib" \
  uv run acm --root /path/to/tirvi --project tirvi ingest --full
```

`scripts/acm-ingest.sh` in this repo is a documentation helper — it
prints the command above with `--root` set to your tirvi checkout
path. Validation: `scripts/validate-ontology.sh` (run before ingest).

After ingestion, query via `mcp__acm__*` MCP tools:
- `acm_search(pattern, project="tirvi")`
- `acm_query_router(query, project="tirvi")` — natural-language search
- `acm_trace(node_id)` — cross-layer walk
- `acm_paths(source, target)` — graph paths
- `acm_untested()`, `acm_high_risk()`, `acm_communities()`, etc.

The `acm-traceability` skill (in `.claude/skills/`) provides a higher-
level interface for cross-layer questions ("which tests cover X?",
"what implements requirement Y?").

## Adding nodes

Each ontology file is YAML. Append nodes under the appropriate top-level
key (e.g., `business_objects:`). Schema files in `ontology/schemas/`
define what fields each node-type requires.

Run `scripts/validate-ontology.sh` after editing to catch:
- Malformed YAML
- Missing required fields
- Duplicate node IDs across files
- Edges with unresolved source/target IDs

Then re-run `scripts/acm-ingest.sh` to refresh the graph.
