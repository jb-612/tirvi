# E10-F04 — Latency Profiling Against ≤ 30 s p50 / ≤ 90 s p95

## Source Basis
- PRD: §7.2 Performance
- HLD: §3 architecture
- Research: src-003 §3 architecture changes #2 + #3 (manifest + min-instances=1); §8.2 latency gate
- Assumptions: ASM05

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P04 SRE | hits NFR | cold-start cost | min-instances=1 |
| P08 Backend Dev | tunes pipeline | hot path uncertain | trace |
| P10 Test Author | benches latency | drift | release gate |

## Collaboration Model
1. Primary: SRE.
2. Supporting: backend dev.
3. System actors: pipeline workers, distributed tracing, latency dashboard.
4. Approvals: ADR-010 cold-start posture.
5. Handoff: latency report → release gate.
6. Failure recovery: budget breach → revert config or scale-up.

## Behavioural Model
- Hesitation: SRE unsure of TF flag scope.
- Rework: bench pages too easy; harder pages added.
- Partial info: cold-start budget uncertain.
- Retry: tracing per stage.

---

## User Stories

### Story 1: Per-stage latency budget enforced

**As an** SRE
**I want** per-stage latency budgets monitored
**So that** the 30 s p50 target holds.

#### Main Flow
1. Tracing per stage; spans aggregate to per-doc latency.
2. Dashboard shows p50/p95.
3. Release gate compares against PRD target.

#### Edge Cases
- Cold-start dominates: gate explicit budget.

#### Acceptance Criteria
```gherkin
Given a 5-page synthetic exam
When the pipeline completes
Then p50 ≤ 30 s and p95 ≤ 90 s
```

#### Dependencies
- DEP-INT to E00-F02 (min-instances), E10-F02 (gates).

#### Non-Functional Considerations
- Cost: min-instances=1 trade-off.

#### Open Questions
- Replay tracing data for offline analysis.

---

### Story 2: Cold-start posture set per environment

**As an** SRE
**I want** dev (min=0) vs prod (min=1) and `--cpu-boost`
**So that** prod meets latency target without dev cost.

#### Main Flow
1. TF workspace config flags applied.
2. Telemetry confirms.

#### Acceptance Criteria
```gherkin
Given prod TF workspace
When the worker scales
Then min-instances=1 and cpu-boost are active
```

#### Dependencies
- DEP-INT to E00-F02.

#### Non-Functional Considerations
- Cost: prod cost adjusted.
