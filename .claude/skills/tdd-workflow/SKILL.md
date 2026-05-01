---
name: tdd-workflow
description: TDD router — validates prerequisites, detects language from task file paths, delegates to @tdd-go or @tdd-flutter. Use --accept-all to skip mode selection in the delegated skill.
user-invocable: true
argument-hint: "[feature-id/task-id] [--accept-all]"
allowed-tools: Read, Glob, Grep, Bash
---

# Role

You are a TDD router. You validate prerequisites, detect the target language
from the task's file paths, and delegate to the language-specific TDD skill.
You do NOT write tests or production code yourself.

# When to Use

- Always use `/tdd` (this skill) as the entry point for TDD work
- It routes to `@tdd-go` or `@tdd-flutter` automatically
- For Python tooling tests, this skill handles inline (rare — Python is
  dev-time only, most Python tests use `@testing` or `@test-functional`)

# When NOT to Use

- **Functional/smoke/regression tests** — use `@test-functional`
- **Designing tests** — use `@test-design`
- **Generating fakes** — use `@test-mock-registry`
- **Running quality gates** — use `@testing`

# Instructions

## Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- `feature-id` — e.g., `N01/F01-db-port`
- `task-id` — e.g., `T03` (optional — if omitted, pick next unchecked task)
- `--accept-all` flag — if present, pass through to delegated skill

## Step 2: Validate Prerequisites

Read in parallel:
1. `.workitems/{feature}/design.md` — must exist
2. `.workitems/{feature}/tasks.md` — must have at least one unchecked
   task per the standard done-marker convention (see below)
3. `.workitems/{feature}/user_stories.md` — must exist

### Task-format contract

Per `.claude/rules/task-format.md`, each task in `tasks.md` is a
`## T-NN: <title>` header followed immediately by a single done-marker
line:

```markdown
## T-NN: <title>

- [ ] **T-NN done**          ← unchecked
- [x] **T-NN done**          ← checked
```

**Producers may vary**: `@design-pipeline` and `@sw-designpipeline`
emit rich per-task metadata (design_element, acceptance_criteria,
ft_anchors, etc.); `@task-breakdown` emits the leaner form. **The
done marker is the same in both.** Read the marker — not any other
status signal — to determine completion state.

For prerequisite validation, the file is acceptable if at least one
`- [ ] **T-NN done**` line exists (i.e. at least one task is
unchecked). If every task is `[x]`, the feature is complete; STOP and
report that no work remains rather than dispatching to TDD.

If any prerequisite fails, STOP and report:

```
TDD Prerequisites FAILED for {feature}:
 - design.md: {present/missing}
 - tasks.md: {has unchecked tasks / all checked / empty / missing}
 - user_stories.md: {present/missing}

Run @design-pipeline (or @sw-designpipeline) first to complete planning.
```

## Step 3: Detect Language

Read the target task from `tasks.md`. Identify the language from file
paths in the task's `test file` or `source file` fields, or from the
feature's location in the project structure:

| Signal | Language | Delegate To |
|--------|----------|-------------|
| `*_test.go`, `cmd/`, `internal/`, `pkg/` | Go | `@tdd-go` |
| `flutter_app/test/`, `flutter_app/lib/`, `*.dart` | Flutter/Dart | `@tdd-flutter` |
| `tests/*.py`, `scripts/*.py`, `tirvi/` | Python | Handle inline (see below) |

If ambiguous (task touches both Go and Dart), report to user and ask which
skill to use.

## Step 4: Delegate

Invoke the language-specific skill, passing the original arguments:

- **Go**: Invoke `@tdd-go {feature-id}/{task-id} [--accept-all]`
- **Flutter**: Invoke `@tdd-flutter {feature-id}/{task-id} [--accept-all]`
- **Python**: See Python section below

The delegated skill handles everything from here: mode selection (bundled vs
strict with its own language-specific decision table), RED/GREEN/REFACTOR
phases, task completion, traceability updates.

## Python Inline

Python may be either dev-time tooling (`scripts/`) or production
application code (`tirvi/`). For Python tasks:

1. Mode default is **bundled** — language skill prompts; user can choose
2. Test files go under `tests/` (mirror the source layout)
3. Run: `pytest tests/ -v -k "test_name"`
4. Three-agent role separation (test-writer / code-writer / refactorer)
   per `.claude/rules/tdd-rules.md` Python table — same as Go/Flutter
5. When tests pass, flip the standard done marker
   `- [ ] **T-NN done**` → `- [x] **T-NN done**` in `tasks.md` (per
   `.claude/rules/task-format.md`)

## What This Skill Does NOT Do

- **Mode selection** — that's the language skill's Step 0
- **Write tests** — that's the language skill's RED phase
- **Write code** — that's the language skill's GREEN phase
- **Set TDD markers** — that's the language skill's agent separation
- **Update traceability** — that's the language skill's task completion

# HITL Gates

This skill has no HITL gates. All gates are in the delegated skills:
- **TDD Mode Selection** — per task, in `@tdd-go` / `@tdd-flutter`
- **Refactor Approval** — advisory, in `@tdd-go` / `@tdd-flutter`
- **Test Failures > 3** — advisory, in `@tdd-go` / `@tdd-flutter`

# Cross-References

- `@tdd-go` — Go TDD with hexagonal test placement, golangci-lint, table-driven tests
- `@tdd-flutter` — Flutter TDD with widget/provider/golden tests, Riverpod overrides
- `@test-functional` — Chicago-school FUNC/SMOKE/REG tests (separate concern)
- `@test-mock-registry` — Shared fake registry for port interfaces
- `@test-design` — Epic-level STD.md and traceability.yaml
- `@testing` — Quality gates runner
- `@design-pipeline` — Source of prerequisites (design.md, tasks.md, user_stories.md)
