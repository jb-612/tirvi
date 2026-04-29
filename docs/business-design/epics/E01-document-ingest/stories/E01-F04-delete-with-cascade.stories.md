# E01-F04 — Delete-With-Cascade

## Source Basis
- PRD: §6.1 (delete removes all artifacts), §8 Privacy
- HLD: §3.4 storage layout; §11 deferred (no auth)
- Research: src-003 §4 R6 (minors' data minimization)
- Assumptions: ASM02 (24h TTL default), ASM07 (anonymous session)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | wants to delete after exam | avoid lingering exam content | one click, full purge |
| P03 Parent | privacy-conscious gatekeeper | wants to verify deletion | "deleted" confirmation message |
| P04 SRE | answers data-deletion request | meets PPL Amendment 13 | audit log of deletion |

## Collaboration Model
1. Primary: student or parent.
2. Supporting: SRE (audit), Lifecycle Manager (TTL backstop).
3. System actors: API delete endpoint, Storage adapter, Audio cache (special handling).
4. Approvals: none for one's own document.
5. Handoff: delete → cascade across `pdfs/pages/plans/manifests/feedback/`; audio reference dropped from manifest, audio object remains shareable per ASM09.
6. Failure recovery: partial cascade retried by lifecycle on next sweep.

## Behavioural Model
- Hesitation: student unsure if delete also removes their feedback.
- Rework: student deletes by mistake; no undo.
- Partial info: confirmation dialog clarifies scope.
- Abandoned flow: tab closes mid-delete; cascade resumes on next request.

---

## User Stories

### Story 1: Student deletes a document and confirms purge

**As a** student
**I want** "delete" to remove the PDF, page JSONs, plans, manifest, and feedback
**So that** my exam content does not linger longer than I want.

#### Preconditions
- Document belongs to the active session.

#### Main Flow
1. Student clicks Delete.
2. UI shows confirmation dialog citing what is deleted (scope shown).
3. API issues `DELETE /documents/{id}`.
4. Worker removes prefixed objects under `pdfs/`, `pages/`, `plans/`, `manifests/`, `feedback/{doc_id}/`.
5. Manifest is removed last; audio cache references dropped (objects retained per ASM09).

#### Alternative Flows
- Bulk delete: coordinator selects 10 documents; cascade per document.

#### Edge Cases
- Delete during active processing: stages cancel; partial outputs purged.
- TTL expiry races user delete: idempotent removal.

#### Acceptance Criteria
```gherkin
Given a document with 5 pages, a manifest, and 2 feedback entries
When the student deletes it
Then within 30 seconds zero objects remain under `pdfs/{doc}`, `pages/{doc}`, `plans/{doc}`, `manifests/{doc}`, `feedback/{doc}`
And the audio cache objects under `audio/{block_hash}` are NOT removed
```

#### Data and Business Objects
- `Document`, `Manifest`, `FeedbackEntry`, `AudioObject` (kept).

#### Dependencies
- DEP-INT to E11-F01 (TTL backstop), E08-F03 (audio cache)

#### Non-Functional Considerations
- Privacy: audit log captures `delete:{doc_id}:{timestamp}` only.
- Reliability: cascade idempotent.
- Performance: cascade ≤ 30 s for typical 5-page doc.

#### Open Questions
- Should an "are you sure?" + 5-second-undo soft-delete be considered?

---

### Story 2: Parent or coordinator requests provable purge

**As a** parent
**I want** to receive evidence that a child's exam content was deleted
**So that** I can satisfy school-paperwork or PPL concerns.

#### Preconditions
- Parent identifier known (consent flow E11-F02).

#### Main Flow
1. Parent issues delete request via UI or email.
2. API runs cascade and emits a deletion certificate (JSON: doc_id, timestamp, hashes purged, retention scope).

#### Edge Cases
- Audio cache retention questioned: certificate explains shareable cache (ASM09).

#### Acceptance Criteria
```gherkin
Given a parent issues a deletion request for their child's documents
When the cascade completes
Then a deletion certificate is returned (or emailed) within 10 minutes
And the certificate enumerates which prefixes were purged
```

#### Dependencies
- DEP-INT to E11-F02 (consent, parent identity), E11-F04 (no-PII logging)

#### Non-Functional Considerations
- Compliance: PPL Amendment 13 storage limitation requires audit-able deletion.
- Privacy: certificate omits document content.

#### Open Questions
- Should certificate be cryptographically signed for tamper-evidence?
