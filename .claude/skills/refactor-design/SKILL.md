---
name: refactor-design
description: Lightweight refactoring design skill — scaffolds workitems, fills design.md and tasks.md from existing research, single HITL gate. Skips user stories and multi-round review since behavior is already pinned by characterization tests.
argument-hint: "[RNN-FNN-feature-name]"
---

Refactor design for $ARGUMENTS:

## Overview

Lightweight 5-step pipeline for refactoring features where:
- Architecture decisions already exist (ADRs, research docs)
- Behavior is pinned by characterization tests
- No new user-facing requirements (code restructuring only)

Produces `design.md` and `tasks.md` — skips `user_stories.md`, diagrams,
and multi-round adversary review. One HITL gate before implementation.

## When to Use

- Refactoring an existing module (extract, decompose, migrate)
- Migration plan and research already exist in `docs/research/`
- Characterization tests cover the target code
- NOT for new features, new APIs, or behavior changes — use `@design-pipeline`

## Step 1: Scaffold Workitem

Create the workitem directory:

```bash
mkdir -p .workitems/$ARGUMENTS
```

Copy only the needed templates:

```bash
cp .workitems/templates/design-template.md .workitems/$ARGUMENTS/design.md
cp .workitems/templates/tasks-template.md .workitems/$ARGUMENTS/tasks.md
```

Do NOT copy `user-stories-template.md` — refactoring has no new user stories.

## Step 2: Gather Context

Read existing research to inform the design. Check these sources in order:

1. **Migration plan**: `docs/research/re-architect/migration-plan.md`
2. **Conclusion**: `docs/research/re-architect/04-conclusion.md`
3. **Component profiles**: `docs/research/component-profiles.md`
4. **Behavioral spec**: `docs/research/behavioral-spec.md`
5. **Test coverage review**: `docs/research/test-coverage-review.md`
6. **ACM graph analysis**: `docs/research/acm-graph-analysis.md`
7. **Relevant ADRs**: `docs/ADR/ADR-*.md`
8. **Target diagrams**: `docs/diagrams/re-architect-*.mmd`
9. **Existing characterization tests**: `tests/unit/test_dashboard*.py`, `tests/characterization/`

Extract from these sources:
- Which functions/modules are being moved or decomposed
- What the target file structure looks like
- What tests already pin the behavior
- What risks the research identified

## Step 3: Fill design.md

Fill the design document. For refactoring, emphasize these sections:

### Required Sections

| Section | Content |
|---------|---------|
| **Overview** | What is being refactored and why (cite migration plan phase) |
| **Interfaces** | Functions being extracted — old location → new location, signature unchanged |
| **Technical Approach** | Extraction strategy, import rewiring, backwards compatibility (if any) |
| **File Structure** | Before/after directory layout |
| **Design Decisions** | Why this decomposition, alternatives from research |
| **Regression Risk** | Which existing behaviors could break — cite specific test files |
| **Characterization Tests** | List test files that pin current behavior, total count, coverage % |
| **Smoke Test** | One command that proves the system still works end-to-end |
| **Rollback Strategy** | How to undo — typically `git revert` since tests catch regressions |
| **Deliverables** | Source → test file mapping table |

### Sections to Skip or Minimize

- **Dependencies**: Only if new packages are needed (e.g., FastAPI)
- **Consumers**: Only if other features depend on this one
- **Risks**: Only non-obvious risks — the research already covers most

### Constraints

- `design.md` must be **≤ 100 lines** (enforced by hook)
- All function signatures must remain unchanged unless the design explicitly changes them
- CC ≤ 5 for all new/modified functions
- Update YAML frontmatter: `id`, `parent_id`, `status: DRAFT`, timestamps

## Step 4: Fill tasks.md

Decompose into atomic tasks using the `@task-breakdown` rules:

### Task Rules for Refactoring

1. **Each task = one file operation**: extract, move, rewire imports, or add tests
2. **Every task must reference a test file** that validates it
3. **"All tests pass" is an acceptance criterion on every task**
4. **No task changes behavior** — only restructures code
5. **< 2 hours per task**, CC ≤ 5 for all modified functions

### Standard Task Sequence for Extraction

For extracting code from a monolith (the most common refactoring pattern):

```
T01: Create target module with extracted functions (copy, don't move yet)
T02: Add unit tests for the new module (import from new location)
T03: Rewire source file to import from new module (remove local copies)
T04: Run full test suite — all existing tests must pass
T05: Clean up — remove dead code, update imports in consumers
```

### Standard Task Sequence for Decomposition

For breaking a large function into smaller ones:

```
T01: Extract helper function N (< CC 5), add to same file
T02: Add unit test for helper function N
T03: Repeat T01-T02 for each helper
T04: Rewrite parent function to call helpers (must stay < CC 5)
T05: Run full test suite — all existing + new tests pass
```

### Constraints

- `tasks.md` must be **≤ 100 lines** (enforced by hook)
- Dependencies must form a DAG (no cycles)
- Include summary table with phase grouping and total estimate

## Step 5: HITL Review Gate

Present the completed `design.md` and `tasks.md` to the user for approval.

Show:
1. **Feature summary** — one sentence
2. **File count** — how many files created/modified
3. **Task count** — total tasks and estimated hours
4. **Test safety** — which test suites pin the refactoring
5. **Risk level** — Low (extraction only) / Medium (interface changes) / High (new deps)

Wait for explicit user approval before proceeding to implementation.

If approved, update `design.md` frontmatter: `status: APPROVED`.
Update `PLAN.md` with the new feature entry.

## After Approval

Implementation uses `@tdd-workflow` working through `tasks.md` in dependency
order. After all tasks complete, run `@verify` for the completion gate.

## Cross-References

- `@design-pipeline` — Full 11-stage pipeline for new features
- `@task-breakdown` — Standalone task decomposition (used internally)
- `@tdd-workflow` — Consumes tasks.md for implementation
- `@verify` — Completion verification after all tasks done
- `@code-review` — Optional post-implementation review
