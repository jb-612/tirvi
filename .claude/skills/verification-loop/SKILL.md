---
name: verification-loop
description: "A comprehensive verification system for Claude Code sessions."
origin: ECC
---

# Verification Loop Skill

A comprehensive verification system for AmdocsBrain sessions.

## When to Use

Invoke this skill:
- After completing a feature or significant code change
- Before creating a PR
- Before marking a Todoist task complete
- Before reporting that work, a brief, or an operational artifact is complete
- After refactoring

## Verification Modes

Choose the modes that match the work. Not every session needs every mode.

### Mode 1: Universal Completion Gate

Run this for **every** completion claim:

1. Check the task or request's success criteria against the actual output.
2. Record the artifact path, link, or exact location.
3. If the work is tracked in Todoist, confirm the live task state.
4. Capture blockers, follow-ups, and residual risks.
5. State evidence confidence as `verified`, `partial`, or `unavailable`.

If any item is missing, the work is not ready to be described as complete.

### Mode 2: Operational Verification

Use this for daily briefs, snapshots, reports, triage, and other workflow
artifacts.

Verify:

- the live sources you relied on were actually queried in this session
- degraded or unavailable sources are called out explicitly
- blockers and waiting-for items came from the latest trusted source
- you separated fact from inference
- the artifact links to the underlying evidence where possible
- the artifact meets the operational snapshot contract when that output is in scope

### Mode 3: Engineering Verification

Use this when files, scripts, or code changed.

Run the repo-relevant checks that apply:

- build
- type check
- lint
- tests
- changed-file review
- targeted security / secret scan

Prefer workspace tools and repo-native commands over generic examples.
If a check does not apply, mark it `N/A` instead of silently skipping it.

## Contract Links

- Todoist lifecycle and close-out semantics: `Core/10_TODOIST_TEAM_WORKFLOW.md`
- Workspace completion gate: `Agents/WORKSPACE-AGENT-OVERLAY.md`
- Operational snapshot contract: `Tools and Skills/Operational-Snapshot/README.md`

## Output Format

After verification, produce a concise report:

```
## Verification Report

- Scope: [what was verified]
- Success criteria: [pass/fail or short note]
- Artifact path: [path or N/A]
- Todoist state: [verified / N/A / issue]
- Source health: [verified / partial / unavailable]
- Engineering checks: [list pass/fail/N/A]
- Residual risks: [none or short list]
- Overall: [ready / not ready]
```

## Continuous Mode

For long sessions, run verification after each meaningful milestone:

```markdown
Set a mental checkpoint:
- After finishing a task
- Before moving a Todoist item to closed
- Before reporting completion to the user
- Before publishing a brief, snapshot, or scorecard update

Run: `/project:verify` or the local verification workflow entrypoint
```

## Integration with Hooks

This skill complements PostToolUse hooks but provides deeper verification.
Hooks catch issues immediately; this skill provides the explicit evidence gate
for accuracy-first completion claims.
