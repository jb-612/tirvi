# tirvi — Claude Code Entry Point

Web app that reads Hebrew exam PDFs aloud for students with reading
accommodations. The defensible layer is **OCR → Hebrew linguistic
interpretation → reading plan → TTS** (not naive OCR + TTS). See
`docs/PRD.md` and `docs/HLD.md`.

Stack (per HLD): Next.js/React frontend, FastAPI on Cloud Run, Cloud
Tasks/Pub-Sub, Cloud Storage, OCR + AlephBERT/YAP/HebPipe + Cloud TTS,
all dev in a single Docker container.

## SDLC Harness Layout

This repo runs under the SDLC harness conventions. Assets live in
`.claude/` and supporting folders at repo root:

| Path | Purpose |
|------|---------|
| `.claude/rules/` | Workflow, TDD, coding/testing rules. Read before non-trivial work. |
| `.claude/agents/` | Subagent definitions (TDD writers/refactorers, reviewers, research). |
| `.claude/skills/` | Skill bundles invoked via `@skill-name` (design-pipeline, tdd-workflow, code-review, ...). |
| `.claude/hooks/` | Shell hooks (TDD separation, complexity check, workitem requirement, dangerous-command block). |
| `.claude/scripts/` | Quality gate + mailbox helpers. |
| `.workitems/` | Per-feature design / stories / tasks / review trails. |
| `ontology/` | Project-level graph slice (business domains, technical implementation, testing, dependencies) — loaded into ACM. |
| `scripts/` | Repo-root scripts: ACM ingest wrapper, ontology validator, per-feature migration helper. |
| `docs/PRD.md`, `docs/HLD.md` | Product + architectural baseline. |
| `docs/research/` | Investigations and prior-art notes. |
| `docs/ADR/` | Architectural decision records. |
| `docs/diagrams/` | Mermaid + exported diagrams. |
| `docs/ideation/` | Single-page idea memos (pre-research). |

## Workflow

Follow `.claude/rules/workflow.md` (the 8-step flow). Quick map:

1. Workplan → 2. Design (`@design-pipeline` / `@sw-designpipeline`,
   `@design-review`, `@test-design`) → 2.5. DDD 7L Scaffold
   (`@ddd-7l-scaffold` for DDD-shaped features; reviewed via
   `@scaffold-review`) → 3. TDD Build (`/tdd` router → `@tdd-go` /
   `@tdd-flutter`; plus `@test-functional`, `@integration-test`) →
4. Code review (`@code-review`) → 5. Feature completion
   (`@feature-completion` / `@verify`) → 6. Commit (`@commit`) →
7. DevOps → 8. Closure.

Skip rules and HITL gates are documented in `.claude/rules/workflow.md`.
For idea capture only, use `@ideation`. For info-only questions, use
`@general-question`.

**Two-skill design**: When `@biz-functional-design` has been run for a
feature (corpus produces `functional-test-plan.md` + `behavioural-test-
plan.md`), Step 2 routes through `@sw-designpipeline` (HLD-driven design
only) instead of re-running PRD-driven story generation. See ADR-013.

## Project Conventions

- **Tests first.** Every new behavior lands with a failing test before
  the implementing commit (`.claude/rules/tdd-rules.md`). **Narrow
  exception:** `@ddd-7l-scaffold` may emit structural shells (folders,
  empty interfaces, classes with `NotImplemented` method bodies, test
  skeletons with skip markers) before TDD; the first real test is
  written by `/tdd` when it activates a skeleton in the GREEN phase.
  Shells contain no behaviour. See ADR-016.
- **Cyclomatic complexity ≤ 5** per function. Split helpers when it
  grows.
- **Conventional commits** with workitem traceability via `@commit`.
- **Never push to git** without explicit user permission.
- **Protected paths** (require HITL before modifying): `CLAUDE.md`,
  `.claude/rules/**`, `.claude/hooks/**`, `.claude/agents/**`,
  `.claude/scripts/**`, `docs/ADR/**`, `.workitems/**`,
  `ontology/**`, `ontology/schemas/**`. See
  `.claude/rules/orchestrator.md`.

## Mailbox

The `mailbox` skill (`.claude/skills/mailbox/`) is Redis-backed and
**off by default**. To enable: run a local Redis (localhost:6379),
configure the Redis MCP server in your client `settings.json`, and
register `.claude/scripts/mailbox-init.sh` as a SessionStart hook.
