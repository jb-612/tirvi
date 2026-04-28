# Claude Code Agents — SDLC Harness Only

This directory contains **software development agents** — Claude Code subagents
for engineering workflows (TDD, code review, debugging, research). They are
project-agnostic and portable to any Claude Code project.

## Available Agents

| Agent | Purpose |
|-------|---------|
| `reviewer.md` | Read-only code reviewer (correctness, security, regressions) |
| `explorer.md` | Read-only codebase explorer (trace execution paths) |
| `debugger.md` | Read-only test failure diagnostics |
| `docs-researcher.md` | Documentation and release-note verifier |
| `tdd-test-writer.md` | TDD RED phase — write one failing test |
| `tdd-code-writer.md` | TDD GREEN phase — minimal code to pass |
| `tdd-refactorer.md` | TDD REFACTOR phase — improve structure |

## Workspace Persona Agents

The 8 workspace persona agents (Shiran, Tonny-Stark, Noah, Noy, Nova, Yasmin,
Pule, Albert) live at their canonical location:

```
Agents/local-agents/<slug>/
├── soul.md          # Core identity
├── identity.md      # Persona description
├── AGENTS.md        # Runtime contract
├── knowledge.md     # Domain knowledge
└── MEMORY.md        # Working memory
```

These personas are dispatched by the workspace mechanisms (slack-listener,
agent-scheduler) which inject persona context into the prompt directly.

### Interactive dispatch via Claude Code

If you want `claude --agent shiran` to work locally, create a personal symlink:

```bash
# For each persona you want available:
ln -s ../../Agents/local-agents/shiran/AGENTS.md .claude/agents/shiran.md
ln -s ../../Agents/local-agents/tonny-stark/AGENTS.md .claude/agents/tonny-stark.md
ln -s ../../Agents/local-agents/noah/AGENTS.md .claude/agents/noah.md
# ... etc
```

These symlinks are `.gitignore`'d — they're per-developer convenience, not
project artifacts.

## Why the Separation?

See `docs/ADR/ADR-003.1-toolkit-skill-colocation.md` for the full rationale.
Short version: workspace persona adapters are not software engineering tools —
mixing them with SDLC agents was a category error.
