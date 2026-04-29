# E01-F02 — Manifest With Conditional Writes: Behavioural Test Plan

## Behavioural Scope
Covers polling cadence, dev confusion around eventual consistency, and SRE
diagnosis when a manifest looks stuck.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Student rapid-refreshing | P01 | rate-limit hits | poll budget |
| Dev assumes single-writer | P08 | race condition | precondition test |
| SRE checks stuck doc | P04 | wasted time | manifest CLI |

---

## Behavioural Scenarios

### BT-025: Student presses refresh repeatedly
**Persona:** P01
**Intent:** see when audio is ready
**Human behaviour:** F5 every second
**System expectation:** API serves cached projection; rate-limit prevents abuse
**Acceptance criteria:** 60 refreshes/min do not destabilize the API

### BT-026: Dev refactors a stage and breaks generation field
**Persona:** P08
**Intent:** add new stage
**Human behaviour:** ignores precondition; writes naively
**System expectation:** integration test red; race-condition reproducer included
**Acceptance criteria:** dev fixes before merge

### BT-027: SRE diagnoses why a 6-page doc has only 5 pages playable
**Persona:** P04
**Intent:** triage
**Human behaviour:** pulls manifest, sees page 4 stuck at NLP-failed
**System expectation:** manifest history shows 3 retries with error code
**Acceptance criteria:** SRE forms hypothesis from manifest alone

## Edge Behaviour
- Browser polls during a manifest GC (TTL boundary); API returns "expired"
  with a clear UX hint.
- Manifest schema version skew: API negotiates which view to return.

## Misuse Behaviour
- Caller tampers with `If-None-Match` headers; ignored; service stays correct.
- Caller polls another session's doc; 404.

## Recovery Behaviour
- Worker fails to write manifest update; next stage retries with the latest
  generation. No double-update.
- Manifest accidentally read 0 bytes (network glitch); reader handles `400`
  by re-reading.

## Collaboration Breakdown Tests
- Two workers race; both retry; one wins per cycle. Behavioural test confirms
  the loser logs `precondition_failed` not `crash`.

## Open Questions
- Do we need a dashboard widget for "manifests stuck > N seconds"?
