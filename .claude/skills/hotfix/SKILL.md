---
name: hotfix
description: Short design cycle for single-file / small-scope bug fixes. Skips @design-pipeline and @design-review (no meeting room, no adversary, no 6-specialist R1), but keeps a 1-page impact note, a 2-reviewer light check, @test-design scoped to the bug, /tdd, @code-review, and a mandatory changelog + GitHub issue close comment on commit.
argument-hint: "[issue-id or brief description]"
disable-model-invocation: false
---

Fix bug $ARGUMENTS via the hotfix lane.

## When to Use

- Single-file / small-scope bug fix
- Regression caught in prod or CI that needs a same-day fix
- Root cause is well-understood; fix is surgical

## When NOT to Use

- Fix touches 3+ modules → use `@design-pipeline` + `@design-review`
- Root cause is unknown → use `@research` or `@deep-research` first
- Fix requires an interface change → goes through full design
- User is adding new behavior, not restoring prior behavior → use `@design-pipeline`

## Instructions

### Step 1: Write the hotfix note

Produce `.workitems/hotfix/{YYYY-MM-DD}-{slug}/hotfix-note.md`:

```markdown
---
title: {one-line title}
issue: {GH issue number, if any}
created: {YYYY-MM-DD}
severity: {critical|high|medium|low}
status: draft
---

## Root cause
{2–4 sentences — what is broken and why}

## Blast radius
- Affected files: {list}
- Affected callers: {list or "none identified"}
- Affected users / environments: {prod | staging | CI | local}

## Fix sketch
{3–6 sentences — what the fix changes. Include a code snippet if < 15 lines}

## Risk
{what could go wrong with this fix — be honest}

## Rollback
{what to revert if fix misbehaves in prod}
```

Keep the note under 80 lines. If it wants to be longer, the fix is not a hotfix — escalate to `@design-pipeline`.

### Step 2: Light review (2 reviewers)

Spawn 2 parallel review agents — **no meeting room, no adversary, no 6-specialist R1**:

1. **Architecture reviewer** — Does the fix sit where it should? Does it respect module boundaries? Is there a cleaner place to fix this? Read `hotfix-note.md` + the fix sketch.
2. **Risk reviewer** — Is the blast radius honest? Is the rollback real? Are there hidden callers the note missed? Read `hotfix-note.md` + grep the affected files' usage sites.

Each reviewer returns: `APPROVE` | `REQUEST_CHANGES` | `ESCALATE` (route to `@design-pipeline`).

If both APPROVE → proceed to Step 3.
If any REQUEST_CHANGES → revise the note, re-review once.
If any ESCALATE → stop the hotfix lane, start `@design-pipeline`.

### Step 3: Scoped test design

Invoke `@test-design` **scoped to the failing case only** — one RED test that reproduces the bug. Do not produce a full STD.md for the module; this is a one-test scope.

Output lands in the same hotfix workitem folder:
- `.workitems/hotfix/{YYYY-MM-DD}-{slug}/test.md` — the failing-case spec (1 test)

### Step 4: RED-GREEN-REFACTOR

Invoke `/tdd` (routes to `@tdd-go` or `@tdd-flutter`):
1. RED — write the failing test from Step 3
2. GREEN — minimum code to pass
3. REFACTOR — optional, advisory only

### Step 5: Code review

Invoke `@code-review` on the hotfix changeset. Full Phase 1 gates (lint, complexity, SAST, etc.) apply. Phase 2 manual review is scoped to the fix diff, not the surrounding module.

### Step 6: Commit with mandatory doc-update

Invoke `@commit`. Commit message MUST include:

1. **Changelog entry** — add a line to `CHANGELOG.md` under `## [Unreleased]` → `### Fixed` with the issue number and 1-line description. If `CHANGELOG.md` is absent, create it with the standard Keep-a-Changelog header.
2. **GitHub issue close comment** — if the hotfix resolves an open issue, post a comment citing the commit SHA + rollback instructions before `gh issue close`.

Both are mandatory. The commit MUST NOT land without both.

Commit type: `fix(<scope>):` per `@commit` conventions.

## No Design Pipeline

This skill deliberately skips:
- `@design-pipeline` (11 stages) — too heavy for a surgical fix
- `@design-review` (3 rounds, 6 specialists, adversary) — replaced by Step 2's 2-reviewer light check
- `@task-breakdown` — the fix is one task

If Step 2 escalates, those skills run instead — in which case the workitem graduates out of `.workitems/hotfix/` into `.workitems/{phase}/{feature-id}/` and the full pipeline takes over.

## Cross-References

- `@test-design` — scoped test for the failing case
- `/tdd` (→ `@tdd-go` / `@tdd-flutter`) — RED-GREEN-REFACTOR
- `@code-review` — Phase 1 gates still apply
- `@commit` — final commit, enforces conventional format
- `@design-pipeline` — escalation target if Step 2 finds the fix is not small-scope
