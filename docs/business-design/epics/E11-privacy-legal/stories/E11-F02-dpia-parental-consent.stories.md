# E11-F02 — DPIA + Parental Consent (≥14)

## Source Basis
- Research: src-003 §4 R6 (PPL Amendment 13 in force 14-Aug-2025; PPA AI Guidelines 2025)
- HLD: §11 deferred auth scope (consent without full auth)
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P03 Parent | gives consent | unclear scope | concise consent UI |
| P01 Student (minor) | uses tool | blocked at gate | smooth flow |
| P04 SRE | runs DPIA | absent | DPIA artifact |

## Collaboration Model
1. Primary: legal lead + product.
2. Supporting: SRE, frontend dev.
3. System actors: consent flow, age estimator (self-declared), DPIA doc.
4. Approvals: legal review.
5. Handoff: DPIA → released artifact.
6. Failure recovery: consent missing → blocked upload.

## Behavioural Model
- Hesitation: parent scrutinizes; FAQ helps.
- Rework: consent text lengthy; lawyer revises.
- Partial info: parent signature delayed; pending state.
- Retry: re-prompt next session.

---

## User Stories

### Story 1: DPIA artifact + parental consent at first use

**As a** legal lead
**I want** a documented DPIA and a parental-consent flow for users ≥ 14 self-declaring as minor
**So that** PPL Amendment 13 is satisfied.

#### Preconditions
- Self-declared age field at first use.

#### Main Flow
1. UI surfaces age screen at first use; minor triggers parent flow (email/sms placeholder).
2. ConsentRecord saved.
3. DPIA published in repo / website.

#### Edge Cases
- Lying about age; legal accepts good-faith self-declare.

#### Acceptance Criteria
```gherkin
Given a self-declared minor at age 15
When the parent submits consent
Then a ConsentRecord is created and the user can upload
```

#### Data and Business Objects
- `ConsentRecord`, `DPIA`.

#### Dependencies
- DEP-INT to E01-F01 (upload gate), E11-F01.

#### Non-Functional Considerations
- Compliance: PPL Amendment 13.
- Privacy: PII in consent stored encrypted.

#### Open Questions
- Threshold age (14 vs 16 vs 18) under Israeli law.

---

### Story 2: Consent revocation

**As a** parent
**I want** to revoke consent and trigger deletion
**So that** I can withdraw at any time.

#### Main Flow
1. Parent clicks revoke (email link or web flow).
2. Cascade per E01-F04 + ConsentRecord marked revoked.

#### Acceptance Criteria
```gherkin
Given consent revocation request
When the cascade runs
Then student documents are deleted within 30 minutes
And the certificate is emailed
```

#### Dependencies
- DEP-INT to E01-F04.

#### Non-Functional Considerations
- Compliance: storage limitation.

#### Open Questions
- Identity verification of revocation requester.
