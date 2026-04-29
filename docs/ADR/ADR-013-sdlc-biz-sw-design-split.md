---
adr_id: ADR-013
title: SDLC harness — biz / sw design split + ACM ingestion
status: Proposed
date: 2026-04-29
deciders: [jbellish, refactor plan option-b-is-basicaly-swirling-panda]
bounded_context: sdlc
hld_refs: []
related_features: [all 47 PLAN.md features; harness-wide]
related_adrs: []
---

# ADR-013 — SDLC harness: biz / sw design split + ACM ingestion

## Status

**Proposed** (2026-04-29). Records PR 0 findings of the refactor plan
`/Users/jbellish/.claude/plans/option-b-is-basicaly-swirling-panda.md`.
Promotes to **Accepted** when PR 4 (smoke test on N00-F03) closes green.

## Context

The `biz-functional-design` skill ran in a Claude.ai cloud session and
wrote 234 markdown + 3 ontology YAMLs to `docs/business-design/epics/
E##-F##/...`, parallel to the existing `.workitems/N##-phase/F##-feature/`
harness. This created two sources of truth and a guaranteed drift surface
when `@design-pipeline` later re-generates `user_stories.md` per
workitem.

PR 0 of the plan asked: where does the existing ACM (Architecture Concept
Model) graph database fit? The audit revealed:

- **ACM is fully operational.** FalkorDB + Elasticsearch + Redis vector
  store, dashboard at `:8741`, MCP server at `:8741/sse`. Three search
  tiers (graph, full-text, vector). Total state: 67,111 nodes /
  63,957 edges across multiple projects.
- **ACM is multi-project.** `acm_stats(project="tirvi")` returns 0/0/0.
  Other projects (`agentic-asdlc`, `axon-workspace`, `agent-context-
  manager`, `mortgage-concierge`, `telecom-solution-portfolio`,
  `ccr5-surv`, `red-alert`, `personal-intelligence`, `shv-sim-swz`)
  are populated. **Tirvi has never been ingested.**
- **An ingest CLI already exists.** `uv run acm --root <path> --project
  <name> ingest --full` with env vars `ACM_GRAPH_NAME`, `ACM_SOURCE_DIRS`,
  `ACM_DOC_DIRS`, `ACM_BACKEND`. Plus an `acm-ingest` skill in another
  project's namespace (`skill:agent-context-manager:acm-ingest`). The
  plan's proposed `scripts/acm-ingest.sh` was duplicating this.
- **The traceability template is already ACM-compatible.** `.workitems/
  templates/traceability.yaml` carries an `acm_nodes:` block with 5 node
  types (`feature`, `spec`, `story`, `criterion`, `task`) and an
  `acm_edges:` block with 5 edge types (`TRACED_TO`, `IMPLEMENTED_BY`,
  `HAS_CRITERION`, `CONTAINS`, `VERIFIED_BY`). Comment header reads:
  *"Filled by @design-pipeline; read by validate-hld-refs.sh and ACM
  ingestion."* The hook is scaffolded; just never run for tirvi.
- **ACM has placeholder layers waiting for population.** `acm_stats()`
  shows the graph supports `domains`, `topics`, `skills`, `agents`,
  `hooks`, `rules` layers — all empty for most projects. Our refactor
  naturally feeds these (biz writes domains, sw writes design/code,
  the harness itself populates skills/agents/hooks/rules).

The "completing existing infrastructure" framing from the plan therefore
holds — but the work is smaller than the plan estimated. Most of the
mechanism exists.

## Decision

1. **Two-skill design model**: `@biz-functional-design` produces business
   artefacts; `@sw-designpipeline` (NEW, extracted from `@design-pipeline`)
   produces software artefacts. `@design-pipeline` becomes a router with
   a Stage 0 detection step.

2. **Ontology lives at repo root** in `ontology/` as 4 layered YAMLs
   (`business-domains.yaml`, `technical-implementation.yaml`,
   `testing.yaml`, `dependencies.yaml`) plus schemas under
   `ontology/schemas/`. This is the project-level slice of the graph;
   per-feature `traceability.yaml` is the feature-level slice. Both feed
   ACM.

3. **ACM ingestion uses the existing CLI**, not a new bespoke script.
   PR 2 adds a thin wrapper script `scripts/acm-ingest.sh` that sets the
   right env vars (`ACM_GRAPH_NAME=tirvi`, `ACM_DOC_DIRS=docs,ontology,
   .workitems`, `ACM_SOURCE_DIRS=cmd,pkg,internal,flutter_app/lib`) and
   calls `uv run acm --root . --project tirvi ingest --full`. It does
   NOT reimplement parsing or graph loading.

4. **Ingest cadence**: run as a `make gate` step (post-test, pre-commit
   advisory). Not a hard pre-commit hook because ACM ingestion takes
   tens of seconds and a failed ACM ingest should not block code commits.
   It runs whenever the developer wants the graph current. CI re-runs
   it after merge.

5. **Node-id namespace alignment**: existing template uses
   `feature:<id>`, `spec:<id>/DE-NN`, `story:<id>/US-NN`,
   `criterion:<id>/US-NN/AC-NN`, `task:<id>/T-NN`. The new layers extend
   this:
   - business-domains: `domain:<DNN>`, `bc:<bounded-context-name>`,
     `persona:<PNN>`, `bo:<BO-NN>` (business object), `co:<CO-NN>`
     (collaboration object).
   - technical-implementation: `module:<name>`, `service:<name>`,
     `port:<name>`, `adapter:<name>`, `class:<name>`, `fn:<name>`,
     `adr:<NNN>`.
   - testing: existing `criterion:` and new `ft:<feature>/<NN>`,
     `bt:<feature>/<NN>` (functional test, behavioural test).
   - dependencies: edges only; new edge types `REALIZES` (sw→biz) and
     `TESTED_BY` (sw→testing).

6. **Migration is lazy, per-feature.** Bulk migration deferred indefinitely.

## Consequences

**Positive**

- Single source of truth for per-feature work (`.workitems/`); single
  source of truth for project-level ontology (`ontology/`).
- ACM finally gets populated for tirvi — unlocks `acm-traceability`
  queries, `acm_untested`, `acm_high_risk`, `acm_communities`, etc., for
  this project.
- Reuses existing ACM CLI; doesn't duplicate parsing or graph-loading code.
- Extracting `@sw-designpipeline` clarifies skill ownership and makes
  parallel feature design less prone to story regeneration.
- Schema-first ontology design forces graphdb-loadability discipline
  from day one.

**Negative**

- 2-week project of skill modifications across 5+ HITL-protected files
  (`.claude/skills/biz-functional-design/`, `design-pipeline/`,
  `test-design/`, `task-breakdown/`, NEW `sw-designpipeline/`). Each
  needs explicit per-file approval.
- Existing `traceability.yaml` template's 5 node/edge types must stay
  compatible while we extend the schema. Forward-compatible additions
  only; no renames.
- 7 skills definitely affected (per audit), 6 possibly affected. Each
  needs a contract test before declaring PR 3 done.
- Story drift risk between corpus and migrated workitem copy; needs a
  `DERIVED FROM <path> @ sha:<hex>` header + drift-check script.

**Neutral**

- Existing ACM operates on multiple projects; tirvi joins the cohort.
  Per-project graph isolation is enforced via `ACM_GRAPH_NAME=tirvi`.
  No risk of cross-contamination with other projects' nodes.

## Alternatives

**A1: Single skill, holistic** (rejected)

Keep `@design-pipeline` as the only skill; embed biz analysis inside it.
Why rejected: tirvi already has 234 markdown + 3 YAMLs of biz output from
the `@biz-functional-design` run. Throwing it away or re-running it as
part of `@design-pipeline` Stage 3 wastes work and contradicts the
existing skill ecosystem (which has `biz-functional-design` as a
first-class skill).

**A2: Embed biz output inline in design-pipeline Stage 3 via a flag**
(rejected)

Modify `@design-pipeline` to accept a `--from-corpus E##-F##` flag that
imports corpus content into the meeting-room phase. Why rejected: bloats
`@design-pipeline` (already 11 stages); biz vs sw concerns are
genuinely different ownership scopes; the `@parallel-features` skill
expects per-skill task tracking that's harder to get right with one
mode-switching skill than with two distinct skills.

**A3: Custom ACM ingest script that bypasses existing CLI** (rejected)

The original plan had `scripts/acm-ingest.sh` reimplementing
node/edge parsing and FalkorDB writes. Why rejected: ACM CLI exists,
is tested, is used by 9 other projects, and accepts our YAML formats
when placed under `ACM_DOC_DIRS`. Building a parallel ingest path is
maintenance burden with no upside.

**A4: Reuse the `acm-ingest` skill from `agent-context-manager` project**
(deferred)

`skill:agent-context-manager:acm-ingest` exists in ACM's index. It
might be directly invocable as `@acm-ingest` from tirvi if its skill
file ships with the ACM toolset. Defer investigation to PR 2; if the
skill is portable, drop the wrapper script and use it directly. If
not, the thin wrapper script is the fallback.

## References

- Refactor plan: `/Users/jbellish/.claude/plans/option-b-is-basicaly-swirling-panda.md`
- ACM help: `mcp__acm__acm_help` (returned via PR 0 verification)
- ACM stats (global): 67,111 nodes, 63,957 edges, 9 known projects
- ACM stats (tirvi): 0 nodes, 0 edges (never ingested)
- Existing traceability template: `.workitems/templates/traceability.yaml`
- Existing skills referencing ACM: `acm-traceability` (in tirvi), and
  the `agent-context-manager` skill family (`acm-ingest`, `acm-explore`,
  `acm-traceability`, `acm-visualize`, `acm-optimize`) seen in the
  cross-project graph.
- Audit findings: 7 skills definitely affected, 6 possibly affected;
  documented in plan §A2 "Cross-skill audit findings".
