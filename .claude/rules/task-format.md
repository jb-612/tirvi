# Task File Format — Producer / Consumer Contract

`tasks.md` is the contract between **task producers** (design skills) and
**task consumers** (TDD skills, completion checkers, and reviewers).
Producers are free to vary the *depth* of per-task metadata; consumers
read a **single standard done marker** per task.

This contract was added to resolve drift discovered when one producer
emitted rich `## T-NN: <title>` header sections without checkboxes while
the consumer expected `- [ ]` lines and silently failed prerequisite
validation.

## The standard done marker

Every task in any `tasks.md` file MUST have exactly one done marker
**immediately after** its task header, on its own line:

```markdown
## T-NN: <imperative verb + what>

- [ ] **T-NN done**

- design_element: DE-NN
- acceptance_criteria: [US-NN/AC-NN]
- ...
```

Rules:

- Marker is `- [ ] **T-NN done**` when the task is not yet complete.
- Marker becomes `- [x] **T-NN done**` once TDD lands the task green.
- The literal task ID (`T-NN`) is duplicated inside the marker so each
  marker is grep-unique (one bold-fenced match per task).
- Marker stays **immediately after** the `## T-NN:` header — no blank
  line elsewhere may intervene.
- Numbering uses `T-NN` (with dash). `TNN` (no dash) is a legacy form;
  consumers MAY accept either, but producers MUST emit `T-NN`.

Consumers locate a task's done state by:

1. Finding the `## T-NN: <title>` header line.
2. Reading the first `- [ ] **T-NN done**` or `- [x] **T-NN done**`
   line *after* that header.
3. If the marker is `[ ]` the task is unchecked; if `[x]` it is done.

## What producers MAY vary

Below the done marker, any structured metadata is permitted. The
standard "rich" form used by `@design-pipeline` /
`@sw-designpipeline` is:

```markdown
## T-NN: <imperative verb + what>

- [ ] **T-NN done**

- design_element: DE-NN
- acceptance_criteria: [US-NN/AC-NN]
- ft_anchors: [FT-NNN]
- bt_anchors: [BT-NNN]
- estimate: 1h
- test_file: tests/unit/test_module.py
- dependencies: [T-NN, T-NN]
- hints: <implementation guidance>
```

Lite producers (e.g., `@task-breakdown`, `@hotfix`) MAY omit metadata
fields and emit just:

```markdown
## T-NN: <title>

- [ ] **T-NN done**

- estimate: 1h
- test_file: tests/...
```

Producers SHOULD prefer the richer form when traceability data
(design_element, ft_anchors) is available; it makes the TDD-time
prompt more concrete.

## What consumers MUST do

| Consumer | Reads | When marker is `[ ]` | When marker is `[x]` |
|---|---|---|---|
| `/tdd` (router) | next-unchecked task | dispatch to language skill | skip, look further |
| `@tdd-go` / `@tdd-flutter` / Python TDD | target task | run the RED/GREEN/REFACTOR cycle | refuse to act (already done) |
| `@feature-completion` / `@verify` | all tasks | flag as remaining work | count toward done |

A consumer that walks `tasks.md` MUST NOT rely on any other "done"
signal (frontmatter `status:`, traceability.yaml `tests[].status`, or
git log) for in-file completion state. Those are derived signals; the
in-file checkbox is the source of truth.

## What CI / hooks MUST do when TDD passes

When the language TDD skill marks a task complete, it:

1. Flips the in-file marker `- [ ] **T-NN done**` →
   `- [x] **T-NN done**`.
2. Optionally updates `traceability.yaml` `tests[].status` to
   `passed` (per ADR-013).
3. Stages the change in the next commit (typically the `tdd: NXX/FYY/
   T-NN green — desc` commit).

## Naming convention

- Task IDs: `T-01`, `T-02`, …, `T-99`. Always two digits, always with
  a dash.
- Task header: `## T-NN: <imperative-verb> <what>`. Two hashes
  (top-level section). Imperative form (`Add`, `Implement`, `Wire`,
  `Refactor`).
- Done marker text: literal `**T-NN done**` (bold, bracketed by
  `**`). Not "complete", not "finished" — `done`.

## Migration of historic files

When this rule ships, all existing `tasks.md` files in
`.workitems/**/tasks.md` are migrated to the new standard via
`.claude/scripts/migrate-task-format.py` (one-shot tool):

- Each `## T-NN:` header gets a `- [ ] **T-NN done**` marker
  inserted immediately after it.
- For tasks already implemented (per `git log --all
  --grep='tdd:.*T-NN green'` matching the feature path), the marker
  is `- [x] **T-NN done**` instead.
- The migration is idempotent: re-running detects existing markers
  and only updates the checked-state.

## When this rule changes

This is a load-bearing cross-skill contract. Changes require:

1. An ADR documenting the change.
2. Coordinated update of every producer and consumer skill in the
   same PR.
3. Migration script for historic files (or explicit "no migration
   needed" rationale in the ADR).
