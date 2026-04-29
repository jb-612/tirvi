# E10-F05 — Cost Telemetry Per Processed Page

## Source Basis
- PRD: §7.4 Cost; §10 Success metrics ($0.02/page target)
- HLD: §10 cost
- Research: src-003 §5 + §8.2 cost gate
- Assumptions: ASM09 (audio cache shareable)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P04 SRE | budget visibility | spike unnoticed | per-page metric |
| P02 Coordinator | bulk-upload cost | unclear | aggregate metric |
| P08 Backend Dev | tunes voices | invisible cost | per-stage metric |

## Collaboration Model
1. Primary: SRE.
2. Supporting: backend dev, finance.
3. System actors: cost telemetry pipeline, billing labels.
4. Approvals: budget alarm threshold via ADR.
5. Handoff: cost dashboard.
6. Failure recovery: spike detection alerts.

## Behavioural Model
- Hesitation: SRE unsure how granular.
- Rework: per-feature label scheme.
- Partial info: GCP billing latency; daily reconciliation.
- Retry: telemetry resilience.

---

## User Stories

### Story 1: Per-page cost computed from telemetry

**As an** SRE
**I want** cost per processed page computed
**So that** I can verify the $0.02 SLO.

#### Main Flow
1. Stage handlers emit characters synthesized, OCR pages processed, etc.
2. Aggregator computes per-page cost.
3. Dashboard shows trend.

#### Edge Cases
- High-cache-hit days; per-page cost low; sanity-check.

#### Acceptance Criteria
```gherkin
Given a 30-day window
When cost is computed
Then per-page cost is ≤ $0.02 amortized
```

#### Dependencies
- DEP-INT to E08-F03 (cache), E07.

#### Non-Functional Considerations
- Reliability: telemetry resilience.

#### Open Questions
- Per-coordinator cost view.

---

### Story 2: Budget alarm

**As an** SRE
**I want** an alarm when monthly cost exceeds budget
**So that** I can investigate before quarter close.

#### Main Flow
1. Monthly forecast vs budget.
2. Alarm at 80% / 100% / 120%.

#### Acceptance Criteria
```gherkin
Given monthly cost reaches 80% budget
When the threshold fires
Then an alarm posts to SRE channel with breakdown
```

#### Dependencies
- DEP-INT to E10-F05 dashboards.

#### Non-Functional Considerations
- Reliability: alarm low-noise.

#### Open Questions
- Per-feature finer-grained alerts.
