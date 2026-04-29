# E00-F01 — Single-Docker Compose: Behavioural Test Plan

## Behavioural Scope
Covers developer behaviour around onboarding, opt-in profiles, and recovery
from RAM / port / credential errors. Internal dev-DX only — no end-user
behaviour.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| First-day clone-and-run | P09 Frontend Dev | abandons if 3+ failures | timed observation, ≤ 5 min to PASS |
| Opt-in profile confusion | P08 Backend Dev | accidentally runs without `models` | UX prompt in error message |
| Resource-edge OOM | P04 SRE / dev | crash mid-up | `make doctor` pre-warning |

---

## Behavioural Scenarios

### BT-001: First-time clone with no docs reading
**Persona:** P09 Frontend Dev
**Intent:** "just run the app"
**Human behaviour simulated:** skips README; types `docker compose up`
**System expectation:** default profile boots without weights; clear warm-up output
**Collaboration expectation:** error messages link to `make doctor` if fail
**Escalation path:** if dev re-runs 3 times unsuccessfully, `make doctor` is offered
**Acceptance criteria:** PASS if dev can open http://localhost:3000 within 5 min

### BT-002: Backend dev forgets to enable models profile
**Persona:** P08 Backend Dev
**Intent:** test NLP changes
**Human behaviour simulated:** runs `docker compose up`; calls `/disambiguate`
**System expectation:** `api` returns 503 with body `{"error": "models profile not active", "fix": "docker compose --profile models up"}`
**Acceptance criteria:** dev recovers without searching docs

### BT-003: Resource pressure during long debug session
**Persona:** P08 Backend Dev
**Intent:** keep stack alive overnight
**Human behaviour simulated:** opens 30 browser tabs; laptop swaps to disk
**System expectation:** `models` healthcheck flips to unhealthy with OOM hint
**Acceptance criteria:** dev sees actionable health output; not a silent hang

### BT-004: Onboarding interrupted (laptop reboot)
**Persona:** P09 Frontend Dev
**Intent:** finish first-day task
**Human behaviour simulated:** kills compose mid-warm-up; reboots
**System expectation:** model weights cached on volume; second `up` reaches healthy in ≤ 30 s
**Acceptance criteria:** dev does not need to re-download weights

## Edge Behaviour
- Repeated `docker compose up && Ctrl-C` cycles in 30 s window do not corrupt
  the model volume.
- Switching from default to `--profile lite` mid-session leaves no orphan
  containers.

## Misuse Behaviour
- Dev edits compose file and uses `--no-deps` to skip a service; doctor still
  exits 0 — flagged as expected limitation in docs.
- Dev mounts host `~/.config/gcloud` into container; permission on read-only is
  preserved.

## Recovery Behaviour
- Compose down with `-v` removes weight volume; dev re-pulls; behavioural test
  confirms warm-up message is clear ("first-run download, ~5 min").
- Network drop during weight download: retry resumes from last byte (HTTP
  range). Behavioural test simulates flaky network.

## Collaboration Breakdown Tests
- New dev cannot reach SRE; the `make doctor` script substitutes for live help
  by pointing at the right docs.
- Two devs share a host (rare); compose project name collision is detected
  with a clear error.

## Open Questions
- Should we ship a one-page "first day" PDF derived from these scenarios?
