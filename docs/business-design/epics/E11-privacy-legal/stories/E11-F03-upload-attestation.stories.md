# E11-F03 — Upload Attestation (No Third-Party Copyright)

## Source Basis
- Research: src-003 §4 R5 (publisher copyright)
- PRD: §8 Privacy
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | uploads exam | uncertain about copyright | clear attestation |
| P02 Coordinator | bulk upload | per-file vs per-session | per-session default |
| P04 SRE | DMCA process | takedown burden | template + workflow |

## Collaboration Model
1. Primary: legal + product.
2. Supporting: SRE.
3. System actors: attestation modal, upload gate, DMCA mailbox.
4. Approvals: legal review.
5. Handoff: attestation → upload allowed.
6. Failure recovery: attestation declined → upload blocked.

## Behavioural Model
- Hesitation: student unsure about exam status.
- Rework: legal updates copy.
- Partial info: takedown received; SRE acts.
- Retry: per-session attestation.

---

## User Stories

### Story 1: Per-session attestation gate before first upload

**As a** student
**I want** a one-time attestation per session that I have permission to upload
**So that** I understand the responsibility.

#### Main Flow
1. First upload triggers modal.
2. User confirms attestation; record stored.
3. Subsequent uploads in session skip the modal.

#### Edge Cases
- Coordinator session — same flow but with extra wording.
- Embedded iframe/SDK blocks modal — upload denied.

#### Acceptance Criteria
```gherkin
Given a fresh session
When the user attempts first upload
Then the attestation modal blocks upload until accepted
And subsequent uploads in the session pass without re-prompt
```

#### Data and Business Objects
- `AttestationRecord`.

#### Dependencies
- DEP-INT to E01-F01.

#### Non-Functional Considerations
- Privacy: attestation log free of PII beyond session ID.

#### Open Questions
- Per-file attestation for high-risk content?

---

### Story 2: DMCA takedown workflow

**As an** SRE
**I want** a documented DMCA workflow
**So that** publisher takedowns are handled within timeframe.

#### Main Flow
1. Mailbox `dmca@tirvi` receives takedown.
2. Workflow: identify object, purge, notify.
3. Audit log per takedown.

#### Acceptance Criteria
```gherkin
Given a DMCA takedown received
When SRE follows the workflow
Then the object is purged within 72 hours
And the takedown record is filed
```

#### Dependencies
- DEP-INT to E01-F04 (cascade).

#### Non-Functional Considerations
- Compliance: legal requirement.

#### Open Questions
- Cross-jurisdictional copyright (Israel + EU + US).
