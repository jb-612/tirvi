---
description: Protected meta files requiring HITL confirmation before modification
---

# Orchestrator — Protected File Policy

Certain files govern the project's behavior, contracts, and development process.
Modifications to these files require HITL (Human-In-The-Loop) confirmation to
prevent accidental governance damage.

## Protected Paths

| Path Pattern | Why Protected |
|-------------|---------------|
| `CLAUDE.md` | Claude Code entry point — changes affect all sessions |
| `AGENTS.md` | Cross-runtime workspace contract |
| `Agents/WORKSPACE-AGENT-OVERLAY.md` | Shared agent behavior contract (~28KB) |
| `.claude/rules/**` | Development governance rules |
| `.claude/hooks/**` | Tool use enforcement hooks |
| `.claude/agents/**` | Subagent definitions |
| `.claude/scripts/**` | Quality gate pipeline |
| `docs/ADR/**` | Architectural decisions |
| `Core/**` | User profile and operating context |
| `pyproject.toml` | Build config and dependencies |
| `.workitems/**` | Feature planning artifacts (design, stories, tasks) |
| `ontology/**` | Project-level graph slice (loaded into ACM); changes affect all features |
| `ontology/schemas/**` | Graph-layer schemas; node/edge type contracts |

## Before Modifying Protected Files

1. State what you intend to change and why
2. Show the diff (dry-run) before applying
3. Wait for explicit user confirmation
4. After modifying, verify nothing else broke (run `make gate`)

## Exceptions

- **Reading** protected files does not require HITL
- **Adding** new files to protected directories is lower risk but still notify
- **Automated formatting** by hooks (auto-ruff-format) is exempt
- **Test files** under `tests/` are not protected

## Contract Update Protocol

When modifying `AGENTS.md`, `WORKSPACE-AGENT-OVERLAY.md`, or `Core/` files:

1. Announce the change scope (which sections, how many lines)
2. Confirm with user before editing
3. After editing, verify all runtimes (Cursor, Codex, Claude Code) would
   interpret the change correctly
4. Note the change in the commit message
