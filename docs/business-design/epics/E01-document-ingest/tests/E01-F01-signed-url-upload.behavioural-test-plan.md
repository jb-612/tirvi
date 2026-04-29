# E01-F01 — Signed-URL Upload: Behavioural Test Plan

## Behavioural Scope
Covers student behaviour during long uploads, multi-tab use, and confusion
about what an upload "means" for privacy.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Privacy hesitation | P01, P03 | bounce | upload tooltip + privacy panel |
| Mid-upload context loss | P01 | retry from 0 | resumable URL |
| Multi-tab same-document | P01 | conflicting state | per-session lock |

---

## Behavioural Scenarios

### BT-021: Student worried about privacy before clicking upload
**Persona:** P01 Dyslexic Student
**Intent:** wants to know what happens to the file
**Human behaviour:** hovers tooltip, opens privacy panel
**System expectation:** copy explains 24h TTL, no third-party analytics, attestation gate
**Acceptance criteria:** student finds answer in ≤ 5 s; conversion measured

### BT-022: Upload interrupted, browser closed, returns 30 min later
**Persona:** P01
**Intent:** finish uploading
**Human behaviour:** comes back; sees "resume?" prompt
**System expectation:** session still valid (within 1 h TTL); resume offered
**Acceptance criteria:** upload resumes from byte offset

### BT-023: Coordinator drags 12 PDFs at once
**Persona:** P02
**Intent:** prep batch for class
**Human behaviour:** drags large set; UI throttles parallel uploads
**System expectation:** queue UI; coordinator can re-order
**Acceptance criteria:** all uploads complete in deterministic order

### BT-024: Student tries multi-tab session
**Persona:** P01
**Intent:** open same doc in 2 tabs
**Human behaviour:** uploads in tab A; tab B shows in-progress state
**System expectation:** tab B sees the same `Document` (session-level)
**Acceptance criteria:** no duplicate upload triggered

## Edge Behaviour
- User pastes file into upload area (no drag); accepted.
- User uploads same file twice; UI offers "you've uploaded this; reuse?"
- User clicks Cancel mid-upload; partial bytes purged within 5 min.

## Misuse Behaviour
- User attempts to upload an .exe renamed to .pdf; rejected at MIME.
- User opens dev tools and overrides client size limit; server still rejects.

## Recovery Behaviour
- User on slow 3G; UI advises switching wifi; tracks per-byte progress.
- Browser crashes mid-upload; resume on next visit within session TTL.

## Collaboration Breakdown Tests
- Coordinator wants to share a doc with a student; not supported in MVP — UI
  surfaces "shareable links not in MVP" so coordinator doesn't try.

## Open Questions
- Should we add a 5-second undo on Cancel?
