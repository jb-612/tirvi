---
name: parallel-features
description: Run design + review + TDD for 2-4 coupled features concurrently via native teams. Each feature gets a dedicated fresh-context designer + runner; team-lead brokers coupling decisions in real-time and runs a consolidated cross-feature review before the user gate. Use when features share contracts, sequencing constraints, or file footprints AND can tolerate parallel execution.
argument-hint: "[feature-id-list]"
---

Parallel feature workflow for $ARGUMENTS.

## When to use

- **2-4 related features** that share coupling (contracts, sequencing hints, or loose file overlap)
- Features are scoped independently enough that a single designer could handle any one, but coupling makes isolated design produce conflicts
- Sequential design + TDD would be slow enough that parallelism is worth the coordination overhead
- You have capacity for 6-8 spawned agents (3-4 designers + 3-4 runners + team-lead)

## When NOT to use

- Single-feature work → use `@design-pipeline` + `/tdd` directly
- Features that are truly independent → parallel is free but cross-feature review is unnecessary
- **Features that share production files with bidirectional edits** → teams run in ONE working directory per official docs; same-file edits overwrite each other. Use `multi-session.md` manual-worktree sessions + mailbox coordination instead.
- Unknown territory with no existing precedent → sequential first to learn the shape

## File-conflict pre-check (mandatory before spawning)

The official docs (<https://code.claude.com/docs/en/agent-teams>) are
explicit: *"Two teammates editing the same file leads to overwrites. Break
the work so each teammate owns a different set of files."* Teammates share
the lead's working directory — there is no per-teammate worktree in native
teams.

Before starting, build a file-collision matrix across the candidate features:

| File | F-A | F-B | F-C | Conflict mode |
|---|---|---|---|---|
| `proto/foo.proto` | ✏️ | ✏️ | — | **HIGH** — two teammates editing same proto → overwrite |
| `internal/bff/handler/foo.go` | ✏️ | ✏️ | — | **HIGH** — same handler file |
| `internal/bff/handler/bar.go` | — | — | ✏️ | — |
| `flutter_app/lib/data/providers.dart` | ✏️ | ✏️ | ✏️ | LOW — append-only new providers |
| `scripts/parity/translation.yaml` | ✏️ | ✏️ | ✏️ | LOW — append-only rows |

- **All HIGH cells can be semantically partitioned?** → teams in one worktree is OK. Assign each teammate a disjoint slice (e.g. F-A owns `GetX`, F-B owns `GetY` of the same `.go` file) + lead brokers the `import` block and struct field merges at commit time.
- **HIGH cells CANNOT be partitioned** (e.g. both features enrich the same message, both edit the same handler method) → **abort teams**, use manual parallel sessions with one `git worktree add` per feature. Coordinate via Redis mailbox per `multi-session.md`.
- **Only LOW cells overlap (append-only)** → teams are the right tool, file conflicts will not bite.

## Prerequisites

- **Feature flag enabled**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `settings.json` env block (agent teams are experimental as of Claude Code v2.1.32)
- **Claude Code v2.1.32+** — verify with `claude --version`
- `@design-pipeline` + `@tdd-workflow` skills exist in the project
- Clean git state on a feature branch
- No other parallel Claude sessions on the same worktree (see `feedback_parallel_session_coordination` memory)
- `TeamCreate`, `TaskCreate`, `SendMessage` tools loaded via ToolSearch
- File-collision pre-check (above) passed — all bidirectional same-file edits are either absent or semantically partitionable

## Workflow

### Stage 1 — Scaffold workitem directories

One per feature under `.workitems/<phase>/<feature-id>/`. Notify as protected-path addition per `orchestrator.md`.

### Stage 2 — Create the native team

```
TeamCreate({team_name: "n<phase>-<feature-group>-design", agent_type: "design-lead"})
```

Team config lands at `~/.claude/teams/<team-name>/config.json`; task list at
`~/.claude/tasks/<team-name>/`. Do not edit these by hand — runtime state
(session IDs, tmux pane IDs) is overwritten on each state update.

Do NOT pass `isolation: "worktree"` to the spawned teammates — teams run
in the lead's working directory by design (per official docs). If you
need worktree isolation, abort and use `multi-session.md` instead.

### Stage 3 — Spawn designers in parallel

One `general-purpose` agent per feature, spawned in a single message with N parallel `Agent` tool calls. Each brief must include:

- Feature scope + motivation
- **Sibling-feature hints** (what other features are being designed in parallel + expected coupling points)
- Reference reading list (prior feature as template, relevant HLD sections, relevant code paths)
- **Explicit instruction NOT to invoke `@design-pipeline`** — avoids nested sub-agent explosion; produce artifacts directly using sibling templates
- Deliverables: `design.md`, `user_stories.md`, `tasks.md`, `test-design.md`, `traceability.yaml`
- Coupling-alert protocol: `SendMessage team-lead` with prefix `CONTRACT_CHANGE:` / `STATUS:` / `BLOCKED:` BEFORE committing to artifacts

### Stage 4 — Real-time coupling resolution (team-lead)

Designers send coupling questions before drafting artifacts. Common decisions:
- Type name locking (e.g. `dispatch-automation`)
- Merge-order constraints
- Source edit strategy (in-place vs functional options vs new type)
- State/idempotency location (Source vs Action vs Store)

Relay decisions back to affected designers via **targeted** `SendMessage` (avoid `*` broadcast — expensive).

### Stage 5 — Consolidated cross-feature review (team-lead)

After all designers ship artifacts, read all `design.md` + `tasks.md` files and run cross-cutting checks:

- **Pre-agreement verification** — did real-time decisions land in artifacts?
- **Contract consistency** — type names, field names, port signatures consistent across features
- **Task ordering conflicts** — three features editing the same file?
- **HLD ref normalization** — one canonical form across all features
- **Test coverage gaps at feature boundaries**
- **File visibility traps** — grep-audit tests (self-destruct tripwires) see working tree, not git index

Write a consolidated review note at `.workitems/<phase>/<feature-group>-consolidated-review.md`. Keep under the workitem hook line limit; split long-form into `meeting-room/` subdirectory if needed.

### Stage 6 — Revisions round

Dispatch revision requests via targeted `SendMessage` with specific blocker/concern labels. Verify landings via direct `grep`/`Read`, not by trusting designer confirmation messages.

### Stage 7 — User gate (mandatory)

Present the unified package to the user with the review findings. Require explicit approval before TDD.

### Stage 8 — Spawn runners in parallel

One `general-purpose` runner per feature into the **same team** (designers stay idle as on-call oracles). Runner briefs must include:

- `tasks.md` path + dependency order
- TDD mode: `/tdd --accept-all` (tasks.md is already atomic; avoid interleaved HITL prompts)
- **TDD Step 0 mandate** — trace end-to-end production path before any code (see `feedback_tdd_process` memory)
- Cross-feature coordination rules (which tasks need sibling signals)
- Stop conditions + final `STATUS:` format
- Silent-discard rule for `task_assignment` routing noise

### Stage 9 — Live coordination (team-lead)

Known failure modes to preemptively brief runners about:

- **TDD marker race** — parallel runners share `/tmp/ba-tdd-markers/<cwd-hash>`. Delete marker, use disciplined write-tests-first. Don't recreate.
- **Working-tree visibility** — grep-audit tests read the filesystem, not the git index. Uncommitted files in guarded directories turn siblings' trees RED. Use out-of-tree `.hold-<feature>/` staging.
- **Team-lead brief cadence lag** — your instructions can go stale between drafting and delivery. Make supersede explicit ("this overrides my earlier X"). Trust runner's reported HEAD over your mental model.
- **Cross-agent commit pollution** — always `git add <specific-files>`, never `-A` or `.`. Use `git reset HEAD -- <sibling-file>` if sibling changes leak into your staged index.
- **File ownership ambiguity** — if two features both need shared infrastructure (e.g. DB lifecycle in `main.go`), assign ownership by **semantic primary consumer**, not by task ordering.

### Stage 10 — Completion verification

Each runner sends a final `STATUS: <feature> TDD complete` with commit hashes + gate results. Team-lead spot-checks:

- `TaskList` shows all tasks completed
- `git log` shows expected commits in expected order
- Byte-identical regression (for extension features) holds
- Abstraction-leak audit cleanliness

### Stage 11 — Session close

- Commit workitem artifacts (separate `design(N<phase>-<feature>)` commits per feature, OR one bundled `design(...)` commit)
- Commit consolidated review note
- Update `.gitignore` for any new build artifacts discovered
- Push branch (**requires user authorization** per CLAUDE.md)
- Update PR
- Shutdown team via `SendMessage shutdown_request` to all teammates

## Anti-patterns learned from N08-F00d/e/f

- **Don't let designers self-initiate runner-level coordination.** Designer peer-DMs are fine for informational heads-up, but decision-making belongs to team-lead.
- **Don't silently discard runner corrections.** When a runner says "your instruction was X", verify the transcript order before assigning blame.
- **Don't retroactively edit `tasks.md` to match runtime reality.** The authoritative interpretation lives in team-lead decision messages, not in revisionist artifact edits.
- **Don't try to fix the TDD marker hook mid-session.** Delete-and-don't-recreate is the simplest correct workaround.
- **Don't assume "no commit yet = no tree impact".** Working tree state is visible to every sibling runner on the same cwd.
- **Don't per-commit escalate to user during TDD.** User's original `parallel tdd team` directive implicitly pre-authorizes TDD cycle commits. Team-lead approves; user approves push at session close.

## Related skills and memories

- `@design-pipeline` — single-feature design
- `@tdd-workflow` / `/tdd` — single-feature TDD
- `@design-review` — standalone design review (can replace Stage 5 for heavier ceremony)
- `.claude/rules/coordination-protocol.md` — three-parallelism-modes decision table
- `.claude/rules/multi-session.md` — manual-worktree + mailbox fallback when teams can't file-partition
- `feedback_parallel_session_coordination` memory — worktree, marker race, grep-audit, brief cadence lag lessons
- `feedback_tdd_process` memory — TDD Step 0 trace discipline
- Official docs: <https://code.claude.com/docs/en/agent-teams> — authoritative reference for team API surface, limitations, and experimental-flag requirement
