# E11-F04 — No-PII Logging Audit

## Source Basis
- PRD: §8 (logs do not contain document content)
- Research: src-003 §7 principle 6
- Assumptions: ASM01, ASM02

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P04 SRE | privacy hygiene | accidental PII in logs | scrubber + audit |
| P12 Security Reviewer | quarterly audit | ad-hoc | scheduled |
| P08 Backend Dev | follows lint | ambiguous fields | clear taxonomy |

## Collaboration Model
1. Primary: SRE + security reviewer.
2. Supporting: backend dev.
3. System actors: log scrubber, audit pipeline, lint rules.
4. Approvals: scrubber rules via review.
5. Handoff: logs → SIEM.
6. Failure recovery: PII detected → ticket + scrubber update.

## Behavioural Model
- Hesitation: dev unsure if a field is PII.
- Rework: scrubber rule false-positive; tightened.
- Partial info: scrubber covers most fields.
- Retry: quarterly audit.

---

## User Stories

### Story 1: Scrubber removes document content from logs

**As an** SRE
**I want** a scrubber that strips potential PII (text bodies, tokens) from logs
**So that** PRD §8 is honored.

#### Main Flow
1. Log emitter wraps in scrubber.
2. Scrubber drops or hashes specific fields.
3. Quarterly audit.

#### Edge Cases
- New field type added; default scrub-allow + dev review.

#### Acceptance Criteria
```gherkin
Given a log entry containing a document content field
When the scrubber runs
Then the field is removed
```

#### Data and Business Objects
- `LogScrubRule`.

#### Dependencies
- DEP-INT to all stages emitting logs.

#### Non-Functional Considerations
- Reliability: scrubber deterministic.

#### Open Questions
- Hashed vs dropped fields.

---

### Story 2: Quarterly audit + remediation

**As a** security reviewer
**I want** a quarterly review of logs for PII drift
**So that** detection is regular.

#### Main Flow
1. Audit pipeline samples logs.
2. Flags suspicious patterns.
3. SRE remediates with PR.

#### Acceptance Criteria
```gherkin
Given a quarterly audit
When suspicious patterns are flagged
Then a remediation PR is required within 1 week
```

#### Dependencies
- DEP-INT to E10-F02 (CI gate on lint).

#### Non-Functional Considerations
- Compliance: audit trail kept ≥ 1 year.

#### Open Questions
- Automated enforcement vs sampling.
