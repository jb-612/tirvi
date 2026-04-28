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
2. `.workitems/{feature}/tasks.md` — must have unchecked tasks (`- [ ]`)
3. `.workitems/{feature}/user_stories.md` — must exist

If any fails, STOP and report:

```
TDD Prerequisites FAILED for {feature}:
 - design.md: {present/missing}
 - tasks.md: {has unchecked tasks / empty / missing}
 - user_stories.md: {present/missing}

Run @design-pipeline first to complete planning.
```

## Step 3: Detect Language

Read the target task from `tasks.md`. Identify the language from file paths
in the task's `test file` or `source file` fields, or from the feature's
location in the project structure:

| Signal | Language | Delegate To |
|--------|----------|-------------|
| `*_test.go`, `cmd/`, `internal/`, `pkg/` | Go | `@tdd-go` |
| `flutter_app/test/`, `flutter_app/lib/`, `*.dart` | Flutter/Dart | `@tdd-flutter` |
| `tests/*.py`, `scripts/*.py` | Python | Handle inline (see below) |

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

## Python Inline (Rare)

Python is dev-time tooling only. For the rare case of TDD on Python scripts:

1. Mode is always **bundled** (Python tooling tasks are specification work)
2. Test files go in `tests/` mirroring `scripts/` structure
3. Run: `pytest tests/ -v -k "test_name"`
4. No separate agent separation — Python is not in the production app path
5. Mark task complete in tasks.md when tests pass

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
