# E01-F04 — Delete-With-Cascade: Functional Test Plan

## Scope
Verifies user-initiated delete cascades across confidential prefixes, leaves
shareable audio cache, and produces an auditable certificate when requested.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E01-F04-S01 | Student delete with cascade | Critical |
| E01-F04-S02 | Parent provable purge | High |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| `DELETE /documents/{id}` | API | S01 | cascades within 30 s |
| Cascade worker | platform | S01 | idempotent removal |
| `DeletionCertificate` | value object | S02 | enumerates purged scope |

---

## Test Scenarios

### FT-044: Cascade removes all confidential prefixes
**Input:** doc with 5 pages, manifest, 2 feedback entries
**Expected:** 0 objects in `pdfs/{doc}/`, `pages/{doc}/`, `plans/{doc}/`, `manifests/{doc}.json`, `feedback/{doc}/`
**Priority:** Critical

### FT-045: Audio cache survives delete
**Input:** delete doc that produced 8 audio blocks
**Expected:** `audio/{block_hash}.mp3` objects still present
**Priority:** High

### FT-046: Idempotent on retry
**Input:** invoke delete twice
**Expected:** second call exits 200 OK with "already gone"
**Priority:** Critical

### FT-047: Cascade during processing cancels stages
**Input:** delete during page 4 NLP
**Expected:** page 4 stage cancels; partial outputs removed
**Priority:** High

### FT-048: Deletion certificate enumerates scope
**Input:** parent requests deletion with certificate
**Expected:** JSON includes prefixes purged + audio retention note
**Priority:** High

### FT-049: Cross-session delete forbidden
**Input:** session B tries to delete session A's doc
**Expected:** 404 (existence not leaked)
**Priority:** Critical

## Negative Tests
- Doc already deleted: 200 idempotent.
- Permission missing on a prefix: surface error; do NOT half-delete silently.

## Boundary Tests
- Doc with 0 pages (upload then immediate delete): cascade idempotent.
- Doc with only manifest (failed before stage 1): cascade still cleans.

## Permission and Role Tests
- Anonymous session can delete only its own doc.
- Parent identity (post E11-F02) can delete child's doc with consent record.

## Integration Tests
- Delete + lifecycle race: idempotent, no errors.

## Audit and Traceability Tests
- Audit log records delete event with doc_id, requester_kind (self|parent), timestamp.
- Certificate signed (post-MVP open question).

## Regression Risks
- Adding a new prefix (e.g., `corrections/`) without updating cascade list.

## Open Questions
- 5-second-undo soft-delete?
