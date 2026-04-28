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

   HITL gates: **Design Review R2** (mandatory if Critical concerns remain),
   **User Gate** (mandatory approval before TDD build).
   For changes touching 3+ modules: **Design approval** (mandatory).

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
| Phase Gate | 5 | All features in phase complete |
| TDD Mode Selection | 3 | Per task — agent recommends bundled or strict |
| Refactor approval | 3 | Advisory — after TDD refactor phase |
| Protected path commit | 6 | Modifying .claude/, docs/, AGENTS.md, WORKSPACE-AGENT-OVERLAY.md |
| DevOps invocation | 7 | Any infrastructure change |
