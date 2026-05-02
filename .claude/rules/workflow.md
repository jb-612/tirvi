---
description: 8-step development workflow with HITL gates and skills
---

# Development Workflow

All feature work follows these 8 sequential steps. Each step has clear actions
and HITL gates defined inline.

## Steps

1. **Workplan** — Interpret user intent, draft high-level plan with scope,
   agents needed, sequencing, and risks. No HITL gate.

2. **Design** — For non-trivial changes: use `@design-pipeline` to scaffold
   workitems, fill design/stories/tasks, run `@design-review` (2 rounds with
   adversary challenge), and `@task-breakdown` for atomic decomposition.
   For daemon work: verify async patterns and shared state implications.

   **Mandatory workitem artifacts** (per the Phase-0 design alignment,
   2026-05-02). Every workitem under `.workitems/<NXX>/<FYY>/` MUST
   contain these files before any code task in the workitem moves to
   `[x] done`:

   | File                       | Purpose                                                          |
   |----------------------------|------------------------------------------------------------------|
   | `design.md`                | Overview, problem, dependencies, interfaces, DEs, OOS, risks      |
   | `tasks.md`                 | T-NN list with the standard done-marker contract (`task-format.md`) |
   | `user_stories.md`          | US-NN with explicit ACs                                          |
   | `traceability.yaml`        | ACM nodes/edges, de_to_hld, ac_to_story, task_to_de              |
   | **`functional-test-plan.md`** | FT-NNN scenarios, negative / boundary / integration / audit; regression risks; open questions |
   | **`behavioural-test-plan.md`**  | BT-NNN persona scenarios, edge / misuse / recovery, collaboration breakdown, open questions |
   | **`ontology-delta.yaml`**       | modules / classes / functions / constants / adr_decisions / tasks added by this feature |

   The latter three are the foundational design assets. They MAY be
   authored as a backfill within the same PR that ships the feature
   code, but they MUST land before merge — no exceptions for "scaffold-
   only" work. F21's workitem is the canonical template for all three.

   See `docs/research/sdlc-shortcut-postmortem-phase0.md` for the
   incident that surfaced this rule and the explicit decision to make
   these artifacts mandatory.

   **Two-skill design (biz → sw)** — When `@biz-functional-design` has been
   run for a feature (presence of `functional-test-plan.md` in the workitem
   folder), `@design-pipeline` Stage 0 detects this and delegates to
   `@sw-designpipeline`, which extracts Stages 2, 2.5, 4, 4b, 5–11 of the
   holistic pipeline and skips PRD-driven story generation (biz already
   wrote `user_stories.md`). When biz has NOT run, `@design-pipeline`
   continues with the holistic flow. See ADR-013.

   **Test planning (always):** Run `@test-design` after stories exist to produce
   STD.md + traceability.yaml (defines WHAT to test — consumed by TDD and
   functional test skills in step 3).

   **Shared fakes (consumer features only):** If port interfaces already exist
   from a prior phase, run `@test-mock-registry` now to generate fakes before
   TDD starts. If this feature IS building the ports (foundational), defer
   `@test-mock-registry` to step 3 after port-writing tasks complete.

   | Feature Type | @test-mock-registry | Why |
   |---|---|---|
   | **Foundational** (building ports) | Step 3, after port tasks | Can't fake interfaces that don't exist yet |
   | **Consumer** (using existing ports) | Step 2, during design | Ports exist, fakes ready before TDD |

   **DDD tactical enrichment (optional):** When `@sw-designpipeline` produces
   a design that implies bounded contexts, aggregates, or domain events, run
   `@ddd-7l-scaffold` after sw-designpipeline and before the User Gate. It
   produces `.workitems/<F>/ddd-design.md` (≤ 200 lines) and appends to
   `traceability.yaml` (existing schema only — `acm_nodes.specs[]`,
   `acm_edges[]`, `de_to_hld{}`). No source code is generated; no ontology
   writes (sw-designpipeline retains sole writer status). Reviewed by
   `@design-review` (not `@code-review` — its Phase 1 quality gate would
   block on intentional design artifacts). The existing User Gate covers
   approval. Skip for hotfixes, docs-only, config-only, or simple features
   with no domain modelling.

   HITL gates: **Design Review R2** (mandatory if Critical concerns remain),
   **User Gate** (mandatory approval before TDD build).
   For changes touching 3+ modules: **Design approval** (mandatory).

2.5. **DDD 7L Scaffold** (optional — DDD-shaped features only) — After
   the Step 2 User Gate clears, use `@ddd-7l-scaffold` to transform
   approved design artefacts into a production-grade, layered code
   scaffold: folders, empty modules, interfaces, port / DTO / result
   types, aggregates / entities / value-objects / events / policies
   (with `NotImplemented` bodies and AC-linked TODOs), test skeleton
   files, DI wiring with fakes, runtime route / handler shells, and the
   `bounded_contexts` block in `traceability.yaml`. **Strict rule:** no
   business logic. The codebase compiles, every test skip is
   intentional, every TODO maps to an AC.

   Skill is portable: `SKILL.md` uses TypeScript as canonical examples;
   per-language reference files at
   `.claude/skills/ddd-7l-scaffold/references/{python,go,dart}.md`
   provide concrete code shapes for that language.

   **Reviews:** 4 staged gates via `@scaffold-review` (NOT
   `@code-review` — its Phase 1 quality gate would block on intentional
   `NotImplemented` failures).

   | Gate | After | Depth | Mandatory |
   |------|-------|-------|-----------|
   | 1 | L1 + L2 (structure + contracts) | Medium | Yes |
   | 2 | L3 (domain model) | Deep | **Yes — most important** |
   | 3 | L4 + L5 (behaviour + TDD readiness) | Deep | Yes |
   | 4 | L6 + L7 (runtime + traceability, final) | Deep | **Yes** |

   **Skip** for: `@hotfix`, docs-only, config-only, trivial features
   with no DDD model (no aggregates, no ports), or features that
   qualify as "scaffolding" per the disqualifiers below.

   HITL gate: **Final Scaffold Review** (Gate 4 above) — TDD cannot
   start until the user approves Gate 4 output. See ADR-016 for
   integration details and deferred ecosystem work.

3. **TDD Build** — Three parallel tracks, dependency-ordered:

   **Track A — Unit tests (sequential per task):**
   Entry point: `/tdd` (router). Validates prerequisites, detects language,
   delegates to `@tdd-go` or `@tdd-flutter`. Language skill evaluates task
   against its decision table, recommends bundled or strict mode, user
   confirms. 3-agent separation (test-writer, code-writer, refactorer).

   **Track B — Functional tests (feature-level, can overlap with Track A):**
   `@test-functional` writes FUNC/SMOKE/REG test code from STD
   traceability.yaml definitions. Tests at public API level — different
   layer than unit tests, so no conflict.

   **Track C — Integration tests (after both sides built):**
   `@integration-test` writes cross-boundary tests. Requires code on both
   sides of a layer boundary to exist (depends on Track A progress).

   **E2E — Deferred:** `@test-design` writes `[ANCHOR]` placeholders only.
   E2E tests require full stack; implemented when infrastructure exists.

   **Foundational features — mock registry mid-step:**
   If `@test-mock-registry` was deferred from step 2 (ports didn't exist),
   run it after port-writing tasks complete and before adapter/service tasks.

   ```
   Foundational (e.g., N01 — building ports):
     T01-T03: /tdd → write port interfaces    ◄── ports now exist
     @test-mock-registry                       ◄── generate fakes
     T04+:    /tdd → adapters, services        ◄── use fakes
     @test-functional                          ◄── FUNC/SMOKE/REG
     @integration-test                         ◄── cross-boundary
   ```

   HITL gates: **TDD Mode Selection** (per task, in language skill),
   **Refactor Approval** (advisory), **Test Failures > 3** (advisory).

4. **Code Review** — Multi-agent parallel review: architecture, code quality +
   security, test coverage. All findings become actionable items. Uses
   `@code-review` skill. No HITL gate.

5. **Feature Completion** — Validates: all tasks complete, tests pass, linter
   clean, complexity check (CC <= 5), interfaces match, docs updated. Uses
   `@feature-completion` skill (or `@verify` for lightweight checks).
   After all features in a phase complete, run `@phase-gate`. No HITL gate
   (phase-gate has its own mandatory HITL).

6. **Commit** — Conventional commit with traceability. Pre-checks: tests pass,
   no secrets staged, no .env files. Uses `@commit` skill. HITL gate:
   **Protected Path Commit** (mandatory for .claude/, docs/, AGENTS.md).

7. **DevOps** — Infrastructure operations (Docker, CI/CD, launchd services).
   HITL gate: **DevOps Invocation** (mandatory).

8. **Closure** — Summarize implementation, note deferred work, update relevant
   docs. No HITL gate.

## When to Skip Steps

| Situation | Skip | Entry skill |
|-----------|------|-------------|
| Bug fix (single file) | Skip step 2 (design-pipeline + design-review) — `@hotfix` runs a short cycle instead | `@hotfix` |
| Docs-only change | Skip steps 3-4 (TDD, review) | `@documentation` |
| Test-only change | Skip step 2 (design) | `/tdd` |
| Scaffolding / config (see disqualifiers below) | Skip steps 2-4 | — |
| Idea capture (pre-research / pre-concept) | Skip steps 2–8 — single-page memo only | `@ideation` |
| Info-only question (no intent to build) | Skip all steps — no artifact unless opted-in | `@general-question` |

### Scaffolding disqualifiers

A feature is **not** scaffolding if any of these are true — run the full
pipeline (`@design-pipeline` → `@test-design` → `/tdd`) instead:

- Introduces new runtime logic (any new `*.go`, `*.dart`, or `*.py` file
  with executable code — not counting pubspec/go.mod edits)
- Adds ≥ 50 lines of new test code across any language
- Adds a new module, package, sub-directory, or helper under `cmd/`,
  `pkg/`, `internal/`, `flutter_app/lib/`, or `scripts/`
- Introduces a new dev dependency that unlocks new code paths (e.g.,
  adding `yaml` to consume YAML files in tests — the dep enables logic)
- Migrates code across a major framework version with breaking changes
  (e.g., Riverpod 2 → 3, regardless of how mechanical the fix feels)

**Qualifies as scaffolding:** pure dependency version bumps, CI/CD tweaks,
Makefile edits, `.gitignore` changes, file-to-file copies without edits,
golangci-lint or ruff config updates. Anything that does not introduce
new callable code.

**Why this section exists:** N05 F02 and F03 both skipped design/TDD
ceremony because "scaffolding" had no objective test. F03 shipped a new
110-line Python normalizer and a new 130-line Dart matcher and still got
self-classified as scaffolding. See
`docs/research/sdlc-guardrail-failures-f02-f03.md` §G4.

## HITL Gate Summary

| Gate | Step | Required When |
|------|------|---------------|
| Design Review R2 | 2 | Critical concerns remain after R1 revision |
| User Gate | 2 | Mandatory approval before TDD build |
| Design approval | 2 | Changes touching 3+ modules |
| Final Scaffold Review | 2.5 | DDD 7L scaffold complete; mandatory before TDD starts |
| Phase Gate | 5 | All features in phase complete |
| TDD Mode Selection | 3 | Per task — agent recommends bundled or strict |
| Refactor approval | 3 | Advisory — after TDD refactor phase |
| Protected path commit | 6 | Modifying .claude/, docs/, AGENTS.md, WORKSPACE-AGENT-OVERLAY.md |
| DevOps invocation | 7 | Any infrastructure change |
