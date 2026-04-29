# E01-F04 — Delete-With-Cascade: Behavioural Test Plan

## Behavioural Scope
Covers user reluctance, parent verification, and audit-friendly delete UX.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Hover-and-doubt | P01 | clicks accidentally | confirm dialog |
| Parent verification | P03 | distrusts SaaS | certificate flow |
| Bulk cleanup | P02 | drains time | multi-select delete |

---

## Behavioural Scenarios

### BT-032: Student hovers Delete then cancels
**Persona:** P01
**Intent:** thinking about cleanup
**Human behaviour:** hovers, hesitates, dismisses
**System expectation:** confirm dialog explains scope
**Acceptance criteria:** no accidental purge

### BT-033: Student deletes wrong document
**Persona:** P01
**Intent:** delete one
**Human behaviour:** hits Delete on the wrong doc
**System expectation:** in MVP, no undo; clear copy "this cannot be undone"
**Escalation path:** support pointer
**Acceptance criteria:** student understands the irreversibility

### BT-034: Parent demands proof of deletion
**Persona:** P03
**Intent:** verification
**Human behaviour:** asks via support email
**System expectation:** support generates certificate via internal tool; parent receives it
**Acceptance criteria:** parent can quote certificate fields

### BT-035: Coordinator bulk deletes after class
**Persona:** P02
**Intent:** clean up class material
**Human behaviour:** multi-selects 10 docs; deletes
**System expectation:** cascade per doc; progress shown
**Acceptance criteria:** all 10 cleaned within 5 min

## Edge Behaviour
- User keeps tab open for a week; 24h TTL silently deleted; UI surfaces a
  clear "this document expired" panel.
- Delete during high system load; cascade queued; UI shows "deleting…".

## Misuse Behaviour
- User attempts to delete via API replay; idempotent.
- User crafts a delete with an invalid doc_id; 404.

## Recovery Behaviour
- Cascade interrupted mid-flow: lifecycle picks up the rest within 24h.
- Audit log unwritable (storage outage): cascade pauses; SRE alerted.

## Collaboration Breakdown Tests
- Parent-initiated delete during student session: student sees "document removed by parent" and a contact link.

## Open Questions
- Should we add a 5-second undo?
