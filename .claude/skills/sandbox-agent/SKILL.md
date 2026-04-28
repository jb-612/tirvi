---
name: sandbox-agent
description: Run a Claude Code coding agent inside a sandboxed Docker container with the claudeium SDLC harness pre-loaded. Use for autonomous coding tasks that need isolation from the host.
argument-hint: "<prompt>"
allowed-tools: Bash, Read, Glob, Grep
---

# Sandbox Agent

Run a Claude Code agent inside a sandboxed Docker container. The agent runs
with `--dangerously-skip-permissions` so it can freely read, write, and execute
inside the container — but cannot affect the host beyond the mounted workspace.

**The image ships the full claudeium harness** (skills, rules, hooks, agents).
On every container start, `sdlc-harness init` scaffolds `.claude/` in the
workspace and the self-signed SANDBOX license is dropped in place, so all
harness skills (including `@ideation`, `@hotfix`, `@general-question`, the
TDD skills, etc.) are immediately available to the sandboxed agent.

## Prerequisites
- Docker must be running
- `ANTHROPIC_API_KEY` must be exported in your shell (sourced from `.env` if present)
- claudeium repo checked out — the Dockerfile + manager script live there

## Workflow

1. **Ensure the sandbox image is built:**
   ```bash
   scripts/sandbox-exec.sh build      # or: make sandbox-build
   ```
   Only needed once (or after claudeium content / Dockerfile changes).
   Check with `docker image inspect sandbox-claude:latest`.

2. **Start the sandbox container** (mounts project root into `/workspace`):
   ```bash
   scripts/sandbox-exec.sh start
   ```

3. **Send the user's prompt** to the sandboxed Claude Code:
   ```bash
   scripts/sandbox-exec.sh prompt "<THE_USER_PROMPT>"
   ```
   - The prompt is the argument passed to this skill
   - Wrap the prompt in double quotes; escape any internal quotes
   - The output is the agent's text response — display it to the user

4. **After the task is done**, stop the container:
   ```bash
   scripts/sandbox-exec.sh stop
   ```

## Rules
- ALWAYS check sandbox status before sending prompts: `scripts/sandbox-exec.sh status`
- If the image doesn't exist, build it first (step 1)
- If the container isn't running, start it (step 2)
- For multi-step tasks, keep the container running between prompts
- If the user says "stop sandbox" or "tear down", run `scripts/sandbox-exec.sh stop`
- Show the user the sandbox agent's full output — do not summarize unless asked
- If the prompt fails, check `scripts/sandbox-exec.sh logs` for diagnostics
- The container has 2 GB RAM and 2 CPUs by default

## Custom Mount
To mount a different directory:
```bash
scripts/sandbox-exec.sh start --mount /path/to/other/project
```

## Running Arbitrary Commands
For debugging or inspection inside the sandbox:
```bash
scripts/sandbox-exec.sh exec ls -la /workspace
scripts/sandbox-exec.sh exec sdlc-harness version
scripts/sandbox-exec.sh exec claude --version
```

## Concurrent Sessions (isolated instances)

`SANDBOX_INSTANCE` lets multiple Claude sessions run isolated sandboxes in
parallel — they share the image but each gets its own container:

```bash
SANDBOX_INSTANCE=review-a scripts/sandbox-exec.sh start --mount /proj/a
SANDBOX_INSTANCE=review-b scripts/sandbox-exec.sh start --mount /proj/b
SANDBOX_INSTANCE=review-a scripts/sandbox-exec.sh prompt "..."    # drives a
SANDBOX_INSTANCE=review-b scripts/sandbox-exec.sh prompt "..."    # drives b
```

When omitted, `SANDBOX_INSTANCE` defaults to `default` — the same single-
container behaviour the script had before parameterization.

## PATH symlink (use from any project)

One-time host setup to make `sandbox-claude` callable from any session:

```bash
make sandbox-install
```

This symlinks `scripts/sandbox-exec.sh` into `~/.local/bin/sandbox-claude`.
Any Claude session on the host can then run:

```bash
sandbox-claude prompt "your prompt"
SANDBOX_INSTANCE=my-session sandbox-claude start --mount "$(pwd)"
```

Without the symlink, use the absolute path to the claudeium repo's script.

## Image Rebuild Cadence
The image bakes in whatever was in `data/` at build time. When claudeium
ships new content (new skills, rule edits, etc.), rebuild the image:

```bash
make sandbox-build
```

## Smoke Test
To verify the image is healthy end-to-end:
```bash
make sandbox-smoke
```
