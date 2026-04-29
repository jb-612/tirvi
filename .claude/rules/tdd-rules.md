---
# Unconditional — always loaded
---

# TDD Discipline

## TDD Entry Point and Mode Selection

Entry point: `/tdd` (router). Validates prerequisites, detects language,
delegates to `@tdd-go` or `@tdd-flutter`.

Each language skill evaluates the task against its own decision table and
prompts: "I recommend {BUNDLED|STRICT} because {reason}. Approve or change?"
Use `--accept-all` to skip the prompt. See `@tdd-go` and `@tdd-flutter`
for language-specific decision tables.

### Bundled Mode (default)

Per task: write ALL tests first, then write ALL code to pass, then refactor.
Test revision pass after GREEN if any test needed signature changes.

### Strict Mode

Per task: write ONE failing test, write minimum code to pass, optionally
refactor. Repeat for each test. Used for tasks with unknown solution shape.

## Core TDD Principles

1. Do not write production code unless it makes a failing test pass
2. Write tests before implementation (bundled or one-at-a-time per mode)
3. Do not write more production code than sufficient to pass the tests

## When to Use TDD

### TDD — for deterministic, testable code:
- Go core engine: config parsing, dispatch logic, repository methods, domain models
- Go BFF: request validation, response shaping, auth middleware
- Go daemons: state management, priority classification, rule-based processing
- Flutter: providers/blocs, use cases, data transformations, repository adapters
- Python tooling: data transformation, calculation logic, API response parsing

**Test with:**
- Go: `go test` with table-driven tests and fakes from `pkg/testutil/fakes/`
- Flutter: `flutter test` with widget tests and provider mocks
- Python: `pytest` with `tmp_path` fixtures

### Functional/Smoke/Regression Tests — written separately:
- Use `@test-design` to produce STD.md + traceability.yaml (WHAT to test).
  When `@biz-functional-design` has run for the feature (presence of
  `functional-test-plan.md`), test-design SYNTHESISES from biz plans
  rather than generating from stories alone. See ADR-013.
- Use `@test-mock-registry` to generate shared fakes from port interfaces
- Use `@test-functional` to write FUNC/SMOKE/REG code (Chicago-school)
- TDD skills handle unit tests only (per-task, from tasks.md)

### Traceability schema (ADR-013):
The per-feature `traceability.yaml` schema is forward-compatible. Existing
`acm_nodes`, `acm_edges`, `de_to_hld`, `story_to_prd`, `task_to_de`,
`ac_to_story` fields are unchanged. New optional fields added by the biz/sw
split: `biz_source.{functional_test_plan_path, behavioural_test_plan_path,
corpus_e_id, imported_at, source_sha}`, `ontology_refs[]` (refs to
`ontology/*.yaml` node IDs), and `tests[].{ontology_id, test_path, status}`
(execution state filled at TDD time). Skills that ignore the new fields
continue to work; TDD skills SHOULD update `tests[].status` as code lands.

### Characterization Tests — for existing untested code:
- Capture current behavior before refactoring
- Pin external API interaction patterns
- Document implicit contracts between components

## Three-Agent Role Separation

During TDD sessions (when `/tmp/ba-tdd-markers/<hash>` exists):

### Go
| Agent | Phase | Can Edit | Cannot Edit |
|-------|-------|----------|-------------|
| tdd-test-writer | RED | `*_test.go` | `*.go` (non-test) |
| tdd-code-writer | GREEN | `*.go` (non-test) | `*_test.go` |
| tdd-refactorer | REFACTOR | both | no new behavior |
| lead | coordination | no `.go` files | all `.go` |

### Flutter/Dart
| Agent | Phase | Can Edit | Cannot Edit |
|-------|-------|----------|-------------|
| tdd-test-writer | RED | `flutter_app/test/**` | `flutter_app/lib/**` |
| tdd-code-writer | GREEN | `flutter_app/lib/**` | `flutter_app/test/**` |
| tdd-refactorer | REFACTOR | both | no new behavior |
| lead | coordination | no `.dart` files | all `.dart` |

### Python (tooling)
| Agent | Phase | Can Edit | Cannot Edit |
|-------|-------|----------|-------------|
| tdd-test-writer | RED | `tests/**/*.py` | `scripts/**/*.py` |
| tdd-code-writer | GREEN | `scripts/**/*.py` | `tests/**/*.py` |
| tdd-refactorer | REFACTOR | both | no new behavior |
| lead | coordination | no `.py` files | all `.py` |

## Test Commands

```bash
# Go
go test ./...                       # all tests
go test -run TestName ./pkg/core/   # single test

# Flutter
flutter test                        # all tests
flutter test test/features/board/   # feature tests

# Python
pytest tests/ -v                    # all tests
pytest -k "test_name" -v            # single test
```

## Complexity Rule

- CC <= 5: Acceptable
- CC 6-7: Must refactor before commit
- CC > 7: Blocked by `check-complexity.sh` hook

## Write Tests Before Implementation

Per CLAUDE.md: before implementing any new behavior or bug fix, write tests
for it first. This applies to all production code in `cmd/`, `pkg/`,
`flutter_app/lib/`, and `scripts/`.
