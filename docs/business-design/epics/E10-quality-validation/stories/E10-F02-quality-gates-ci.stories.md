# E10-F02 — OCR / NLP / TTS Quality Gates In CI

## Source Basis
- Research: src-003 §8.2 quality gates
- HLD: §3.3 worker pipeline
- Assumptions: ASM06

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P04 SRE | release gate | regressions slip | per-stage gate |
| P10 Test Author | trusts gates | flaky | deterministic |
| P08 Backend Dev | passes gates | unclear failure | clear messages |

## Collaboration Model
1. Primary: SRE.
2. Supporting: test author.
3. System actors: CI runner, bench, baseline store.
4. Approvals: threshold change via ADR.
5. Handoff: gate result → PR comment / merge block.
6. Failure recovery: gate failure → PR blocked unless waiver.

## Behavioural Model
- Hesitation: dev uncertain about waiver.
- Rework: threshold tuned after MOS update.
- Partial info: bench page added; baseline must reset.
- Retry: 3-run median absorbs noise.

---

## User Stories

### Story 1: Per-stage gates fail PR on regression

**As an** SRE
**I want** OCR, NLP, diacritization, G2P, and TTS quality gates wired in CI
**So that** regressions cannot land silently.

#### Main Flow
1. CI runs bench on changed-stage adapters.
2. Compares against last-green baseline.
3. Fails if MVP gate breached.

#### Edge Cases
- Bench fixtures updated; baseline reset.
- Statistical noise; 3-run median.

#### Acceptance Criteria
```gherkin
Given a PR that increases NLP error rate above gate
When CI runs
Then PR is blocked with a clear message
```

#### Dependencies
- DEP-INT to E02-F06, E10-F01, E00-F04.

#### Non-Functional Considerations
- Reliability: gate deterministic.
- DX: PR comment with link to dashboard.

#### Open Questions
- Per-stage threshold table location.

---

### Story 2: Quality dashboard shows historical metrics

**As a** stakeholder
**I want** a dashboard of historical metrics
**So that** I can see quality trends.

#### Main Flow
1. Bench results published to dashboard per release.
2. Trends per metric per adapter.

#### Acceptance Criteria
```gherkin
Given 10 releases of bench history
When the dashboard renders
Then per-adapter trend lines show direction over time
```

#### Dependencies
- DEP-INT to E10-F01.

#### Non-Functional Considerations
- Privacy: dashboard internal only.
