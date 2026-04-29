# E10-F04 — Latency Profiling: Functional Test Plan

## Scope
Verifies per-stage latency budgets, cold-start posture, dashboard.

## Source User Stories
- S01 budgets — Critical
- S02 cold-start posture — High

## Test Scenarios
- **FT-281** 5-page exam p50 ≤ 30 s. Critical.
- **FT-282** 5-page exam p95 ≤ 90 s. Critical.
- **FT-283** Per-stage spans aggregated. High.
- **FT-284** Prod min-instances=1 verified. Critical.
- **FT-285** Dev min-instances=0 verified. High.
- **FT-286** Dashboard shows trends. High.

## Negative Tests
- Bench infra cold; latency exceeds; alarm.

## Boundary Tests
- 1-page p50 ≤ 6 s; 50-page p50 ≤ 5 min.

## Permission and Role Tests
- Tracing data not user-visible.

## Integration Tests
- E00-F02 ↔ E10-F04.

## Audit and Traceability Tests
- Per-stage latency logged anonymized.

## Regression Risks
- Worker scaling change; bench catches.

## Open Questions
- Replay tracing for offline.
