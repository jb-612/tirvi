# E01-F05 — Bucket Lifecycle Rules: Behavioural Test Plan

## Behavioural Scope
Covers parent / student trust, SRE config drift, and the "did it really
delete?" question.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Trust verification | P03 | parent skepticism | sweep audit |
| Opt-in confusion | P01 | accidental long retention | clear UI |
| SRE drift | P04 | lifecycle silently disabled | nightly drift check |

---

## Behavioural Scenarios

### BT-036: Parent asks "is the file really gone in 24h?"
**Persona:** P03
**Intent:** trust verification
**Human behaviour:** reads FAQ; checks timestamp
**System expectation:** docs cite the 24h ± 1h tolerance; FAQ links audit log
**Acceptance criteria:** parent satisfied without escalation

### BT-037: Student opts in to 7-day, forgets
**Persona:** P01
**Intent:** keep for the week
**Human behaviour:** toggles on, never toggles off
**System expectation:** auto-revert to 24h after 7d; UI surfaces the change
**Acceptance criteria:** student is not surprised

### BT-038: SRE finds lifecycle rule manually disabled
**Persona:** P04
**Intent:** routine ops
**Human behaviour:** runs nightly drift check
**System expectation:** drift detected; PR opened to re-enable
**Escalation path:** if lifecycle disabled > 24h, page on-call
**Acceptance criteria:** rule re-enabled within 4 h

### BT-039: Student notices doc gone earlier than expected
**Persona:** P01
**Intent:** continue studying
**Human behaviour:** opens doc; sees expired
**System expectation:** UI explains 24h tolerance; offers re-upload
**Acceptance criteria:** student understands; re-uploads

## Edge Behaviour
- Lifecycle sweep skipped due to GCS regional issue; tolerance 25h becomes 30h
  for one event; behavioural test confirms support guidance.
- Concurrent user delete + lifecycle delete: idempotent.

## Misuse Behaviour
- User attempts to extend retention via API tampering; rejected.
- Coordinator wants to keep class material 30d; offers post-MVP "library
  mode" — currently surfaced as "not in MVP".

## Recovery Behaviour
- TF apply forgets a prefix; lifecycle leaves objects orphaned; manual cleanup
  script + ADR.
- After PPL violation report, audit reveals delayed lifecycle; corrective
  ADR + retro.

## Collaboration Breakdown Tests
- Privacy reviewer questions audio cache retention; behavioural test confirms
  FAQ + ADR link is one click away.

## Open Questions
- Lifecycle alarm thresholds — page on what skew?
