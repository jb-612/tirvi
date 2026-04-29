# E01-F01 — Signed-URL Upload Flow

## Source Basis
- PRD: §6.1 Upload & document handling, §7.4 Cost
- HLD: §3.2 Endpoints `POST /uploads`, `POST /documents`; §9 Data flow
- Research: src-003 §10 Phase 1 F1.1
- Assumptions: ASM07 (anonymous session)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Dyslexic Student | uploads exam PDF | upload finishes fast on home wifi | failed uploads retry from scratch | resumable signed URL |
| P02 Coordinator | uploads practice material | bulk upload several PDFs | one bad file blocks the rest | per-file isolation |
| P07 Anonymous Session | system actor | scope upload to session | cross-session access | session-keyed prefix |

## Collaboration Model
1. Primary: student.
2. Supporting: coordinator (bulk-upload mode); SRE (lifecycle).
3. System actors: API (`POST /uploads`), Storage adapter, Manifest coordinator.
4. Approvals: copyright attestation gate (E11-F03) before first upload.
5. Handoff: signed URL → browser → GCS → `POST /documents`.
6. Failure recovery: resumable upload; partial bytes preserved.

## Behavioural Model
- Hesitation: student unsure if upload privacy is safe; reads tooltip.
- Rework: file > 50 MB; re-tries with smaller export.
- Partial info: PDF-only restriction not visible until pick-time.
- Abandoned flow: tab closes mid-upload; on next visit, "resume?" prompt.
- Retry: flaky wifi; resumable upload picks up byte offset.

---

## User Stories

### Story 1: Student uploads a 50 MB exam over flaky wifi

**As a** dyslexic student
**I want** my upload to resume after a network drop
**So that** I don't lose progress when commuting wifi flakes out.

#### Preconditions
- Browser session active; copyright attestation accepted.
- File ≤ 50 MB; MIME `application/pdf`.

#### Main Flow
1. Browser POSTs `/uploads` with file metadata (size, hash).
2. API returns signed resumable URL (TTL 1 h) + upload session ID.
3. Browser uploads in chunks to GCS resumable endpoint.
4. On network drop, browser queries upload status; resumes from offset.
5. On success, browser POSTs `/documents` with object key.

#### Alternative Flows
- Student aborts mid-upload; session auto-expires after 1 h.
- Student switches devices; resume blocked (session-bound) — by design.

#### Edge Cases
- File renamed to `.pdf` but is image: server-side MIME sniff rejects.
- File exactly 50 MB: accepted; 50.0001 MB: rejected with size message.
- ZIP-bomb-style PDF (huge text repetition): policy gate downstream.

#### Acceptance Criteria
```gherkin
Given a 30 MB PDF and a flaky wifi connection
When the upload is interrupted at 60% and then resumed
Then the resume completes without re-sending the first 60%
And the resulting `Document` shows `status=uploaded`
```

#### Data and Business Objects
- `Document` (id, hash, size, status, uploaded_at, session_id)
- `UploadSession` (id, ttl, byte_offset)
- `RetentionPolicy` (24h default per ASM02)

#### Dependencies
- DEP-INT to E01-F02 (manifest), E11-F01 (TTL), E11-F03 (attestation)
- DEP-EXT GCS resumable upload

#### Non-Functional Considerations
- Performance: 50 MB upload over 10 Mbps connects in ≤ 50 s nominal.
- Privacy: object key includes session ID; no cross-session access.
- Reliability: resume window 1 h.
- Auditability: upload begin/end events logged without document content.

#### Open Questions
- Do we expose a hash to the browser pre-upload to enable client-side dedup?

---

### Story 2: Coordinator uploads multiple practice PDFs

**As an** accommodation coordinator
**I want** to upload several PDFs in one session
**So that** I can prep practice material for a class group.

#### Preconditions
- Coordinator role indicator (UI flag; no auth in MVP).
- Copyright attestation accepted once per session.

#### Main Flow
1. Coordinator drags 5 PDFs into upload area.
2. Browser opens 5 parallel signed-URL requests (≤ 3 concurrent).
3. Each PDF lands as its own `Document`.

#### Alternative Flows
- One file fails MIME check; others succeed; per-file error UI.

#### Edge Cases
- Total batch > 250 MB; UI surfaces a per-batch advisory.

#### Acceptance Criteria
```gherkin
Given 5 valid PDFs are dragged into the upload area
When uploads complete
Then 5 distinct `Document`s exist, each with status `uploaded`
And one PDF failure does not roll back the other 4
```

#### Dependencies
- DEP-INT to E11-F03 (attestation once per session)

#### Non-Functional Considerations
- Performance: parallelism ≤ 3 per browser limit.
- Accessibility: keyboard alternative to drag-drop required.

#### Open Questions
- Should batch upload share a single attestation or require per-file?
