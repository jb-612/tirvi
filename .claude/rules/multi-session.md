---
description: Rules for running multiple Claude Code sessions against the same repository — worktree isolation, mailbox coordination, TDD marker invariants
---

# Multi-Session Coordination

Running two or more Claude Code sessions against the same local repo is
supported **only under the conditions in this rule**. Violating any rule
below has caused silent state corruption in practice — see
`feedback_parallel_session_coordination.md` in memory.

## Core invariant

**One physical working directory → one active session.** Two sessions
must not share a working directory, even if they think they are on
different branches. Git's HEAD is per-worktree, not per-session; any
`git checkout` from one session instantly flips the other session's
on-disk state.

## Worktree requirement

Before a second session starts work on the same repo:

```bash
git worktree add ~/VSProjects/<project>-<scope> <branch>
# Then in the second session:
cd ~/VSProjects/<project>-<scope>
```

The `<scope>` suffix names the feature or phase the second session owns
(e.g., `tirvi-adr15`, `tirvi-n08`). Never reuse the bare project name
(e.g., `tirvi`) for a worktree path — that's reserved for the primary
working directory.

**Marker hash check:** the TDD role enforcement marker at
`/tmp/ba-tdd-markers/<hash>` is keyed by `shasum` of the working
directory path, not by branch. Separate worktrees produce different
hashes, which is what isolates the two sessions' TDD state. A single
shared worktree produces ONE marker file that both sessions overwrite.

## Session-start checklist

Every session must run these at start and whenever a long pause resumes:

1. `git rev-parse --abbrev-ref HEAD` — verify you're on the expected branch
2. `pwd` — verify you're in the expected working directory
3. `git worktree list` — verify the worktree layout matches expectations
4. `~/.claude/scripts/mailbox-read.sh --folder internal | head -30` — pick
   up any coordination requests from the other session

If the working directory has flipped to an unexpected branch (e.g., you
see commits in `git log` that you didn't make), STOP. Do not dispatch
TDD agents, do not edit files. Send a mailbox coordination request to
the other session, wait for acknowledgment, then recover via `git
checkout <expected-branch>` and `git worktree add` for the intruder's
branch at a new path.

## Mailbox coordination

The `mailbox:<project>:internal` Redis stream (for tirvi:
`mailbox:tirvi:internal`) is the inter-session communication channel. Use it **before** any branch operation that
could affect a shared worktree, and **whenever** one session needs a
commitment from the other.

### Message kinds

| Kind | Script | Use for |
|---|---|---|
| `info` | `~/.claude/scripts/mailbox-send.sh --folder internal --kind info` | Status updates (fire-and-forget) |
| `action` | `~/.claude/scripts/mailbox-send.sh --folder internal --kind action` | Requests that need the other session to DO something; tracked as pending until marked complete |
| `response` | `mcp__redis__xadd` direct (script does not support this kind) | Threaded replies to an action or question; include `ref_id` field pointing at the parent stream ID |

### Thread walking

Messages with a `ref_id` field are replies to that parent. Include a
`ref_id` on every response so threads remain walkable after days of
mailbox accumulation.

### Session naming convention

Use a human-readable scope, not an auto-generated UUID:
- Good: `F05h-page-migration-session`, `N08-F00-engine-consolidation-session`
- Bad: `session-abc123`, `claude-worker-5`

## Branch scoping rules

1. **Main branch** is owned by the primary session running production
   migration work. That session commits and pushes to `origin/main`.
2. **Feature branches** are owned by secondary sessions working on
   parallel scope (ADRs, engine consolidation, experimental features).
   That session commits and pushes to `origin/<feature-branch>`.
3. **Neither session may push to `origin/main` without coordination**
   if the other session is mid-commit.
4. **A secondary session must never `git checkout main` on its own
   worktree**. If it needs to see main state, use `git log origin/main`
   or `git worktree add` a third worktree for reference.
5. **The primary session must never `git checkout <feature-branch>`
   on the main worktree**. If it needs to inspect the other session's
   work, read from the feature branch's worktree directly.

## What to do on coordination failure

If a session discovers it's on the wrong branch/worktree (via the
session-start checklist, a system-reminder about external file
modification, or an unexplained `git status`):

1. **Do not panic, do not force anything.** Git is more reliable than
   both sessions' shared memory.
2. Check `git reflog | head -20` — understand what happened and when.
3. Check `git worktree list` — know all active worktrees.
4. Send a mailbox action request to the other session stating what
   you observe and what you need (e.g., "you appear to have flipped
   my worktree to your branch mid-TDD; please pause while I recover
   via git checkout back to main").
5. Wait for acknowledgment via mailbox response.
6. Recover: `git checkout` back to your expected branch; uncommitted
   files typically survive the flip if they don't conflict with the
   destination branch's tree.
7. Checkpoint-commit any in-flight work to protect it from further
   interference.
8. If possible, add a git worktree for the other session to move to,
   and send them the new path via mailbox.

## Clock skew

Two sessions often have different `date` values (e.g., one at
2026-04-10, one at 2026-04-11). This is not a bug; Redis stream IDs
are server-side and authoritative. Use stream IDs for ordering, not
the `ts` field in message bodies.

## Related

- Memory: `feedback_parallel_session_coordination.md` — worked recovery example
- Memory: `feedback_mailbox_protocol.md` — script vs direct xadd gotchas
- Memory: `feedback_parallel_session_reflog.md` — earlier session's reflog panic debugging
- Rule: `coordination-protocol.md` — in-session team coordination (different scope)
