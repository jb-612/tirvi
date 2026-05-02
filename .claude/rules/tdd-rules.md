---
# Unconditional — always loaded. Language-agnostic. Per-language TDD
# skills (`@tdd-go`, `@tdd-flutter`, `@tdd-python`, …) own concrete
# path matrices and command examples; this file owns the universal
# discipline.
---

# TDD Discipline

This rule is **language-agnostic**. The principles below apply to every
project, every language. The harness ships per-language TDD skills
(under `.claude/skills/tdd-*`) that bind these principles to concrete
file paths and test runners. The hosting project's `CLAUDE.md`
declares which languages apply; the agent must inspect the actual
repository before invoking any per-language path matrix from this
file or its associated skills.

## TDD Entry Point and Mode Selection

Entry point: **`/tdd`** (router). The router:

1. Validates prerequisites (workitem exists, design artifacts in
   place per `.claude/rules/workflow.md`, current task is the next
   unchecked one in `tasks.md`).
2. Detects the language(s) at play by inspecting the task's
   `test_file` path and the project's CLAUDE.md.
3. Delegates to the matching per-language TDD skill (e.g.,
   `@tdd-go`, `@tdd-flutter`, `@tdd-python`). The harness must NOT
   hard-code which delegation is correct for any given project.

Each per-language TDD skill evaluates the task against its own
decision table and prompts: *"I recommend {BUNDLED|STRICT} because
{reason}. Approve or change?"* Use `--accept-all` to skip the
prompt. See the per-language skill SKILL.md files for their
decision tables.

### Bundled Mode (default)

Per task: write ALL tests first, then write ALL code to pass, then
refactor. Test revision pass after GREEN if any test needed signature
changes.

### Strict Mode

Per task: write ONE failing test, write minimum code to pass,
optionally refactor. Repeat for each test. Used for tasks with
unknown solution shape.

## Core TDD Principles (universal)

1. Do not write production code unless it makes a failing test
   pass.
2. Write tests before implementation (bundled or one-at-a-time per
   mode).
3. Do not write more production code than sufficient to pass the
   tests.
4. Per-task `tasks.md` markers (`- [ ] **T-NN done**` →
   `- [x] **T-NN done**`) flip atomically with the GREEN commit per
   `task-format.md`.

## When to Use TDD (universal)

### TDD — for deterministic, testable code

Anything that's a pure function, a state machine, a parser, a
formatter, a configuration loader, a request validator, a domain
model. Per-language TDD skills enumerate concrete examples for the
languages they cover.

### Functional / Smoke / Regression tests — written separately

- Use `@test-design` to produce STD.md + traceability.yaml (defines
  WHAT to test). When `@biz-functional-design` has run for the
  feature (presence of `functional-test-plan.md`), test-design
  SYNTHESISES from biz plans rather than generating from stories
  alone. See ADR-013.
- Use `@test-mock-registry` to generate shared fakes from port
  interfaces.
- Use `@test-functional` to write FUNC/SMOKE/REG code (Chicago-
  school).
- Per-language TDD skills handle UNIT tests only (per-task, from
  tasks.md); functional tests are the language-agnostic concern of
  `@test-functional`.

### Traceability schema (ADR-013)

The per-feature `traceability.yaml` schema is forward-compatible.
Existing `acm_nodes`, `acm_edges`, `de_to_hld`, `story_to_prd`,
`task_to_de`, `ac_to_story` fields are unchanged. New optional
fields added by the biz/sw split: `biz_source.{functional_test_plan_path,
behavioural_test_plan_path, corpus_e_id, imported_at, source_sha}`,
`ontology_refs[]` (refs to `ontology/*.yaml` node IDs), and
`tests[].{ontology_id, test_path, status}` (execution state filled
at TDD time). Skills that ignore the new fields continue to work;
TDD skills SHOULD update `tests[].status` as code lands.

### Characterization Tests — for existing untested code

- Capture current behavior before refactoring.
- Pin external API interaction patterns.
- Document implicit contracts between components.

## Three-Agent Role Separation (universal pattern)

During TDD sessions (when `/tmp/ba-tdd-markers/<hash>` exists), the
harness enforces a three-agent split. The principle is universal;
the per-language path matrix is owned by the corresponding TDD
skill. Generic shape:

| Agent           | Phase    | Can edit                         | Cannot edit                    |
|-----------------|----------|----------------------------------|--------------------------------|
| tdd-test-writer | RED      | test files (per language convention) | non-test source files       |
| tdd-code-writer | GREEN    | non-test source files            | test files                     |
| tdd-refactorer  | REFACTOR | both                             | no new behavior                |
| lead            | coordination | no source files in this language | all source files in this language |

**Per-language path matrices live in the matching TDD skill's
SKILL.md** (e.g., `.claude/skills/tdd-go/SKILL.md`,
`.claude/skills/tdd-flutter/SKILL.md`, `.claude/skills/tdd-python/SKILL.md`).
The `enforce-tdd-separation.sh` hook reads the marker file and
delegates path-validation to the active language's matrix.

## Test Commands (per the language's TDD skill, NOT this rule)

This rule does NOT enumerate test commands per language — that's the
per-language TDD skill's responsibility. Generic shape:

```bash
# <runner> for the project's language
<runner> [args]                  # all tests
<runner> [filter] [args]         # single test or pattern
```

Common runners include: `go test`, `flutter test`, `pytest`, `vitest`,
`bun test`, `cargo test`, etc. The agent must read the project's
CLAUDE.md or `package.json` / `pyproject.toml` / `go.mod` to learn
which runner applies before running.

## Complexity Rule (universal)

- CC ≤ 5: Acceptable.
- CC 6-7: Must refactor before commit.
- CC > 7: Blocked by `check-complexity.sh` hook.

## Write Tests Before Implementation (universal)

Per CLAUDE.md (project): before implementing any new behavior or bug
fix, write tests for it first. This applies to all production code
in whatever directories the project's CLAUDE.md declares as
"production code roots" (commonly `cmd/`, `pkg/`, `src/`, `tirvi/`,
`flutter_app/lib/`, `lib/`, `scripts/`, etc. — varies per project).

The agent **must inspect the project's actual layout** (via
`Glob`, `ls`, or by reading the project's CLAUDE.md) before
declaring a path as a production code root. Pattern-matching from
the harness — "this looks like a project that has a Flutter app"
— has caused real design errors. See
`docs/research/sdlc-shortcut-postmortem-phase0.md §lesson 5`.
