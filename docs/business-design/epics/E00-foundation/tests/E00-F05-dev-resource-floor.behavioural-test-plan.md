# E00-F05 — Dev Resource Floor: Behavioural Test Plan

## Behavioural Scope
Covers developer behaviour under resource pressure and confusion about which
profile to run.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Skips doctor; runs full stack | P09 Frontend Dev | OOM frustration | doctor PASS gate documented |
| Misreads PASS/FAIL output | P08 Backend Dev | takes wrong action | clear next-step lines |
| Onboards with old laptop | new joiner | drops out | lite profile path |

---

## Behavioural Scenarios

### BT-017: Frontend dev runs full stack and OOMs
**Persona:** P09 Frontend Dev
**Intent:** preview the player
**Human behaviour:** `docker compose --profile models up` on 8 GB host
**System expectation:** model service OOMs; doctor link in error output
**Acceptance criteria:** dev runs `make doctor`, switches to lite

### BT-018: Backend dev needs models for a one-off
**Persona:** P08 Backend Dev with light laptop
**Intent:** test a Hebrew-NLP fix
**Human behaviour:** runs `--profile models` knowing it's tight
**System expectation:** model service runs; warns RAM-low; allows the run
**Acceptance criteria:** dev completes the test, then exits

### BT-019: New joiner on old laptop
**Persona:** new dev with 8 GB MacBook
**Intent:** finish first day
**Human behaviour:** runs `make doctor` first
**System expectation:** doctor recommends lite; dev follows path; productive in 30 min

### BT-020: Doctor flagged FAIL but dev ignores
**Persona:** P08 Backend Dev
**Intent:** test "just one quick thing"
**Human behaviour:** ignores FAIL and runs full stack
**System expectation:** services boot; OOM eventually; logs cite "doctor warned"
**Acceptance criteria:** dev links to doctor output in their bug report

## Edge Behaviour
- Doctor PASSes one minute, FAILs the next (background task started); doctor
  recommends re-running closer to compose-up.
- Profile switched mid-session leaves orphan containers; doctor command shows
  an "orphans detected" line.

## Misuse Behaviour
- Dev edits doctor thresholds locally; CI lints the canonical thresholds.
- Dev runs `docker compose down` without `-v`; weight volume preserved (good).

## Recovery Behaviour
- Doctor PASS-then-FAIL across reboot: simply re-run; thresholds stable.
- After OOM crash, dev runs lite; doctor confirms safe.

## Collaboration Breakdown Tests
- SRE not available to update doctor on a new laptop class; interim manual
  override flag (`--force`) documented but flagged in audit.

## Open Questions
- Should doctor talk to the team's anonymized telemetry to refine thresholds?
