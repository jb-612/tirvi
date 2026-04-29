# E10-F03 — Blind MOS Study (Dyslexic Teen Panel)

## Source Basis
- PRD: §10 metrics; §11 risks acknowledged
- Research: src-003 §4 R2; §8.2 MOS gate ≥ 3.5
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P05 MOS Panel Participant | rates samples | bias | blind protocol |
| P12 MOS Panel Orchestrator | runs study | drift | versioned protocol |
| P04 SRE | data quality | small panel | n=10 baseline |

## Collaboration Model
1. Primary: orchestrator (research lead).
2. Supporting: panel participants, ethics review.
3. System actors: blind sample server, rating capture, voice routing.
4. Approvals: ethics review + parental consent (≥14).
5. Handoff: ratings → quality dashboard.
6. Failure recovery: invalid ratings discarded.

## Behavioural Model
- Hesitation: participants unsure about protocol.
- Rework: ratings inconsistent; orchestrator clarifies.
- Partial info: limited sample sets per participant.
- Retry: cross-panel review.

---

## User Stories

### Story 1: Run blind MOS study (n=10) on bench bagrut samples

**As a** research lead
**I want** to run a blind MOS study before MVP launch
**So that** "≥ 90% pronunciation" claims are evidence-backed (R2).

#### Preconditions
- Ethics approval; parental consent.
- Voice samples generated from same SSML across providers.

#### Main Flow
1. Participants rate 5-point Likert across multiple bagrut passages.
2. Anonymized; aggregated; per-voice scores reported.

#### Edge Cases
- One participant outlier; sensitivity analysis.

#### Acceptance Criteria
```gherkin
Given a panel of 10 participants and 30 samples
When ratings are aggregated
Then per-voice MOS ≥ 3.5 to pass MVP gate
```

#### Data and Business Objects
- `MOSStudy`, `MOSRating`, `Participant` (anonymized).

#### Dependencies
- DEP-INT to E07-F04 (voice routing decisions), E10-F02 (gates).

#### Non-Functional Considerations
- Privacy: PII minimized; ratings without identifiers.
- Compliance: ethics approval recorded.

#### Open Questions
- Panel size scaling for v1.

---

### Story 2: Sample server distributes blind sets

**As a** orchestrator
**I want** a sample server that randomizes voice / order
**So that** bias is minimized.

#### Main Flow
1. Server emits per-participant set with random voice + sample order.
2. Logs only voice metadata, never participant audio.

#### Acceptance Criteria
```gherkin
Given two participants
When samples are distributed
Then voice and order differ across participants
```

#### Dependencies
- DEP-INT to E07.

#### Non-Functional Considerations
- Privacy: zero PII captured.

#### Open Questions
- Pre-screen participants for hearing acuity.
