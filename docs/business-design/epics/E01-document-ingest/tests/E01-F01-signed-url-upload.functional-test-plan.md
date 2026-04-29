# E01-F01 — Signed-URL Upload: Functional Test Plan

## Scope
Verifies signed-URL handout, resumable upload, MIME enforcement, size cap, and
batch upload isolation. Out of scope: copyright attestation (E11-F03).

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E01-F01-S01 | Resumable upload over flaky wifi | Critical |
| E01-F01-S02 | Coordinator bulk upload | High |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| `POST /uploads` | API | S01 | returns signed resumable URL within 200 ms |
| `Document` | aggregate | S01, S02 | unique per upload session |
| `UploadSession` | value object | S01 | TTL 1h, byte-offset tracked |

---

## Test Scenarios

### FT-028: Signed URL TTL is 1 hour
**Input:** call `/uploads` at T; query GCS at T+59 min
**Expected:** signed URL still valid; T+61 min returns 403
**Priority:** Critical

### FT-029: Resume from byte offset
**Input:** upload 30 MB; cut at 60%; resume
**Expected:** resume completes from byte 18 MB; total content matches hash
**Priority:** Critical

### FT-030: Size cap enforced
**Input:** 51 MB PDF
**Expected:** API returns 413 with size message
**Priority:** Critical

### FT-031: MIME sniff rejects fake-PDF
**Input:** file renamed `.pdf` from `.png`
**Expected:** server-side sniff returns 415
**Priority:** Critical

### FT-032: Bulk upload, 1 fails, 4 succeed
**Input:** 5 files, file 3 over size limit
**Expected:** 4 `Document`s created; error per file 3
**Priority:** High

### FT-033: Cross-session isolation
**Input:** session A creates doc; session B tries `GET /documents/{id}`
**Expected:** 404 (not 403) to avoid leaking existence
**Priority:** Critical

## Negative Tests
- Forged signed URL (modified TTL): GCS rejects.
- Replayed completed-upload notification: API idempotent.
- File 0 bytes: rejected.

## Boundary Tests
- 50 MB exact: accepted; 50.0001 MB: rejected.
- 1 KB minimum: accepted (typical 1-page).
- Hash collision (extremely rare): treated as new doc, not dedup, in MVP.

## Permission and Role Tests
- Anonymous session creates document; another session cannot see it.

## Integration Tests
- Browser → API → GCS (resumable): single upload session crosses three actors.
- API → Manifest (E01-F02): document creation triggers manifest write.

## Audit and Traceability Tests
- Upload begin/end events logged with session_id, doc_id, byte counts only.

## Regression Risks
- Adding chunked-upload variant that bypasses MIME sniff.

## Open Questions
- Should we expose hash on the client to enable client-side dedup?
