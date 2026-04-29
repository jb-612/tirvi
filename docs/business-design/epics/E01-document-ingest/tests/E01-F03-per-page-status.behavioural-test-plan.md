# E01-F03 — Per-Page Status: Behavioural Test Plan

## Behavioural Scope
Covers students reacting to partial availability, coordinators tracking batch
progress, and SREs diagnosing stuck pages.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Impatience for first audio | P01 | abandons | progressive UI |
| Partial doc anxiety | P01 | thinks doc broken | clear progress chips |
| Bulk progress tracking | P02 | scope blindness | per-doc summary list |
| SRE triage | P04 | slow MTTR | manifest CLI |

---

## Behavioural Scenarios

### BT-028: Student waits 25 s; first audio plays
**Persona:** P01
**Intent:** start studying
**Human behaviour:** uploads, watches progress
**System expectation:** first block playable < 30 s p50
**Acceptance criteria:** student begins playback without rage-refreshing

### BT-029: Page 3 shows red; student panics
**Persona:** P01
**Intent:** finish exam
**Human behaviour:** sees error chip on page 3
**System expectation:** UI labels error as "this page didn't read; try retry"
**Escalation path:** retry button visible; help link if retry also fails
**Acceptance criteria:** student does not assume the whole doc is broken

### BT-030: Coordinator monitors a 10-doc batch
**Persona:** P02
**Intent:** prep before class
**Human behaviour:** scans status grid
**System expectation:** per-doc progress visible at a glance
**Acceptance criteria:** coordinator identifies which 2 docs are stuck in 10 s

### BT-031: SRE diagnoses with CLI
**Persona:** P04
**Intent:** explain stuck doc to user
**Human behaviour:** tirvi-cli manifest <doc>
**System expectation:** timeline reveals NLP retried 3× with `OOM`
**Acceptance criteria:** root cause identified without reading raw GCS

## Edge Behaviour
- Network drop between polls: UI surfaces "checking..." not "failed".
- Browser tab backgrounded; UI uses `Page Visibility` to slow polling.

## Misuse Behaviour
- Student floods retry: rate-limit prevents abuse.
- Coordinator opens 10 tabs to monitor; UI works but warns about API budget.

## Recovery Behaviour
- After SRE fixes a stage bug, mass-retry script restarts only failed pages.
- After temporary outage, polling auto-resumes when API reachable.

## Collaboration Breakdown Tests
- SRE on call but CLI broken: fallback is gcloud + manifest schema doc.
- Student cannot reach support; in-app FAQ explains failure scenarios.

## Open Questions
- Should student see SRE-style timeline in a "details" expander?
