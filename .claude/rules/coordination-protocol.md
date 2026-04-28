---
description: Team coordination protocol for multi-agent collaboration
---

# Coordination Protocol

## Three parallelism modes — pick the right tool

Claude Code offers three distinct mechanisms for parallel work. They are NOT
interchangeable; the wrong choice produces file overwrites, merge thrash, or
lost coordination signals. Reference:
<https://code.claude.com/docs/en/agent-teams>.

| Mode | What it is | Working directory | Coordination | Use when |
|---|---|---|---|---|
| **Subagents** | `Agent` tool without `team_name`. Within the parent session. | Parent's cwd (or `isolation: "worktree"` for an isolated copy) | Result summarized back to parent only | Quick focused research, verification, or exploration tasks where only the result matters. Fire-and-report. |
| **Agent teams** | `Agent` with `team_name`, coordinated via `TeamCreate` + `SendMessage` + shared task list. Experimental. | **Shared** — all teammates run in the lead session's cwd | Peer-to-peer messaging, shared task list, lead brokers coupling decisions | 2-4 coupled features with **file-disjoint** footprints, where teammates need to discuss / challenge / coordinate mid-flight |
| **Manual parallel sessions** | Human opens N Claude Code sessions, each in its own `git worktree add`'d directory. No team. | **Isolated** — one worktree per session | Mailbox (Redis stream) or pull request comments; no automated coordination | Features that **share production files** (e.g. both edit `agent.proto` + `agent.go`), or work that must isolate TDD markers + grep-audit tests from siblings |

**Decision gate when planning parallel work:**

1. Do the candidate features **share files** that will be edited simultaneously? → **manual parallel sessions** via `multi-session.md`. Teams in the same worktree will silently overwrite each other.
2. Are features file-disjoint AND would benefit from peer-to-peer coordination? → **agent teams** via `@parallel-features`.
3. Is the parallel work a short research/verification task with a single return value? → **subagents** (no team, optionally `isolation: "worktree"` for an isolated copy).

## Native Teams (primary for file-disjoint parallel work)

Claude Code's agent-teams feature is **experimental**; enable it explicitly:

```json settings.json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

Requires Claude Code **v2.1.32+**. Verify with `claude --version`.

- `TeamCreate` — Create a team with shared task list (lead only)
- `SendMessage` — Direct messages between teammates (fire-and-forget; no awaitable reply)
- `TaskCreate/TaskUpdate` — Shared task tracking with dependencies (file-lock based race resolution)
- `Agent` with `team_name` — Spawn a teammate joining that team

**Teammates share the lead's working directory** per the official docs
(<https://code.claude.com/docs/en/agent-teams#avoid-file-conflicts>). Do NOT
combine `team_name` with `isolation: "worktree"` — the documented pattern is
file-disjoint teammates sharing one cwd. If file isolation is required, use
**manual parallel sessions** (see `multi-session.md`) instead.

## Team Constraints

- Keep teams small (2-4 teammates; 5-6 tasks per teammate is the sweet spot)
- One team per session, no nested teams, lead is fixed
- Teammates inherit session permissions and hook guardrails **at spawn time** (per-teammate mode can be changed after)
- All HITL gates remain in effect for teammates (permission prompts bubble up to the lead)
- Session resume (`/resume`, `/rewind`) does NOT restore in-process teammates — re-spawn if resuming
- Team config at `~/.claude/teams/{team-name}/config.json`; task list at `~/.claude/tasks/{team-name}/`

## Message Prefixes

Prefix `SendMessage` content with these tags for clarity:

| Prefix | When to use |
|--------|-------------|
| `STATUS:` | Progress update — what's done, what's next |
| `BLOCKED:` | Cannot proceed — need input or dependency resolution |
| `CONTRACT_CHANGE:` | Proposing a change to shared interfaces or contracts |
| `BUILD_BROKEN:` | Tests failing — all teammates should be aware (broadcast) |
| `BUILD_FIXED:` | Tests green again — safe to resume (broadcast) |

## Enforcement

1. **PreToolUse hooks** — Block forbidden file edits (TDD role separation,
   protected file policy)
2. **Quality gate** — Run before commit; blocks if tests fail
3. **Task ownership** — Each task has one owner; check `TaskList` before
   claiming work

## TDD Role Separation

During TDD sessions the marker file at `/tmp/ba-tdd-markers/<hash>` gates
which role can edit which files. The hash is `shasum` of the working
directory path, so **separate worktrees isolate TDD state automatically** —
in-session parallel subagents in ONE worktree share the marker (race
hazard; see `@parallel-features` skill Stage 9 and
`feedback_parallel_session_coordination` memory).

Language-specific edit matrices (Go, Dart, Python) live in
`.claude/rules/tdd-rules.md` — this is the canonical reference. The
`enforce-tdd-separation.sh` hook reads the marker and enforces per-language
path restrictions.
