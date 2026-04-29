# E11-F01 — 24h TTL + Lifecycle Automation

## Source Basis
- PRD: §8 Privacy
- HLD: §3.4 storage; §11 deferred Cloud SQL
- Research: src-003 §4 R3+R7, §10 Phase 5 F11.1; ADR-005
- Assumptions: ASM02

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P03 Parent | privacy-first | minors data lingering | 24h default |
| P04 SRE | enforces | drift | TF-managed |
| P01 Student | opt-in extends | accidental loss | clear UX |

## Collaboration Model
1. Primary: SRE.
2. Supporting: legal advisor (PPL Amendment 13).
3. System actors: GCS lifecycle, manifest TTL fields.
4. Approvals: ADR-005.
5. Handoff: lifecycle config to E01-F05.
6. Failure recovery: drift detector raises PR.

## Behavioural Model
- Hesitation: SRE unsure if exemption (audio cache) acceptable.
- Rework: privacy reviewer revises ADR.
- Partial info: ADR text lags policy change.
- Retry: nightly drift checks.

---

## User Stories

### Story 1: Lifecycle config enforces 24h on confidential prefixes

**As an** SRE
**I want** the bucket lifecycle config to enforce 24h on `pdfs/`, `pages/`, `plans/`, `manifests/`, `feedback/`
**So that** PPL Amendment 13 storage limitation is honored.

#### Main Flow
1. TF lifecycle rules apply.
2. Drift detector verifies daily.

#### Acceptance Criteria
```gherkin
Given a daily drift run
When config matches policy
Then drift detector reports green
```

#### Dependencies
- DEP-INT to E00-F02 (TF), E01-F05.

#### Non-Functional Considerations
- Compliance: PPL Amendment 13 + PPA AI Guidelines 2025.

#### Open Questions
- Is audio cache exemption acceptable to legal?

---

### Story 2: TTL extension opt-in

**As a** student
**I want** opt-in 7-day retention with parental re-consent for minors
**So that** I can keep practice material across a study week.

#### Main Flow
1. Student toggles 7-day; if minor, prompt parent re-consent.
2. ConsentRecord saved.

#### Edge Cases
- Parent declines; opt-in cancelled; doc reverts to 24h.

#### Acceptance Criteria
```gherkin
Given a minor toggles 7-day retention
When the system detects minor age
Then parent consent flow triggers
And opt-in only applied after consent
```

#### Dependencies
- DEP-INT to E11-F02 (consent), E01-F05.

#### Non-Functional Considerations
- Compliance: minors' consent.

#### Open Questions
- Age threshold for parental consent (14? 18?).
