# E01-F05 — Bucket Lifecycle Rules (24h TTL)

## Source Basis
- PRD: §8 Privacy ("auto-delete after configurable TTL"), §6.1
- HLD: §3.4 storage layout (lifecycle rules)
- Research: src-003 §4 R3 R7, §10 Phase 1 F1.5; ADR-005 slot
- Assumptions: ASM02 (24h default; 7-day opt-in)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P03 Parent | wants short retention | minors' data risk | 24h default visible |
| P04 SRE | configures lifecycle | drift between code & bucket | TF-managed only |
| P01 Student | wants longer retention sometimes | studying over week | opt-in 7-day mode |

## Collaboration Model
1. Primary: SRE (config); Lifecycle Manager (enforces).
2. Supporting: parent / student (visibility into policy).
3. System actors: GCS lifecycle, Lifecycle Manager, manifest TTL fields.
4. Approvals: TTL change is an ADR-005-class decision; non-trivial.
5. Handoff: TTL policy → bucket lifecycle config → object metadata.
6. Failure recovery: lifecycle delays surfaced via SRE dashboard.

## Behavioural Model
- Hesitation: student worried about losing content; opts into 7 days.
- Rework: SRE sees a missed prefix; updates TF; re-applies.
- Partial info: parent unaware of audio cache exception (ASM09); FAQ explains.
- Abandoned flow: student opts in then forgets; auto-revert at 7d.

---

## User Stories

### Story 1: Default 24h TTL applied to confidential prefixes

**As an** SRE
**I want** GCS lifecycle rules to expire `pdfs/`, `pages/`, `plans/`, `manifests/`, `feedback/` after 24 hours
**So that** confidential exam content auto-deletes per ASM02.

#### Preconditions
- TF workspace applied.

#### Main Flow
1. TF defines lifecycle rule: prefix in {pdfs, pages, plans, manifests, feedback} → AGE > 24h → DELETE.
2. Bucket carries the rule on apply.
3. Lifecycle runs daily; observable via Cloud Logging.

#### Alternative Flows
- Audio cache (`audio/`) carries no rule (shareable, content-hashed).

#### Edge Cases
- A document opted into 7-day retention (per Story 2): manifest sets `retention=7d`; lifecycle skips on `metadata.retention=7d`.
- Bucket lifecycle race with user delete: idempotent.

#### Acceptance Criteria
```gherkin
Given the dev bucket has applied lifecycle rules
When 25 hours pass since a PDF upload
Then the PDF object is gone
And the audio cache objects are unchanged
```

#### Data and Business Objects
- `RetentionPolicy` (default=24h, opt-in=7d).
- `Document.retention_mode`.

#### Dependencies
- DEP-INT to E11-F01 (privacy lifecycle), E00-F02 (TF skeleton).

#### Non-Functional Considerations
- Compliance: PPL Amendment 13 storage limitation.
- Reliability: lifecycle action observed in audit log.

#### Open Questions
- Is the audio cache exemption acceptable to a privacy reviewer? Re-evaluate.

---

### Story 2: Student opts in to 7-day retention

**As a** student
**I want** to keep an uploaded exam for up to 7 days
**So that** I can revisit during a study period.

#### Preconditions
- Student is logged in to a session that supports the opt-in.

#### Main Flow
1. Student toggles "keep for 7 days" before processing starts.
2. API sets `Document.retention_mode = 7d`; manifest carries field.
3. Lifecycle skips matching objects until 7-day boundary.
4. UI shows a clear countdown.

#### Alternative Flows
- Student turns off opt-in mid-week; reverts to 24h from change time.

#### Edge Cases
- Multiple devices view the same document; opt-in is per-document, not per-device.

#### Acceptance Criteria
```gherkin
Given a student opts a document into 7-day retention
When 25 hours pass
Then the document is still present
And after 7 days + 1 hour the document is gone
```

#### Dependencies
- DEP-INT to E11-F01 (24h base policy).

#### Non-Functional Considerations
- Privacy: opt-in disclosed in UI with privacy-impact note.
- Reliability: countdown reflects actual lifecycle timing.

#### Open Questions
- Does opt-in require parental re-consent for minors?
