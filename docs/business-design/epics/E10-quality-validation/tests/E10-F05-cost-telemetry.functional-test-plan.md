# E10-F05 — Cost Telemetry: Functional Test Plan

## Scope
Verifies cost computation, cache contribution, alarms.

## Source User Stories
- S01 per-page cost — Critical
- S02 budget alarms — High

## Test Scenarios
- **FT-287** Per-page cost ≤ $0.02 amortized. Critical.
- **FT-288** Cache contribution ≥ 25% hit rate after 7d. Critical.
- **FT-289** Forecast vs budget alarms (80/100/120%). High.
- **FT-290** Per-feature billing labels propagate. High.
- **FT-291** Daily reconciliation with GCP billing. High.

## Negative Tests
- Telemetry pipeline outage; alarm via separate channel.

## Boundary Tests
- Quiet day low cost; busy day high cost.

## Permission and Role Tests
- Cost dashboards limited to SRE + finance.

## Integration Tests
- Cost ↔ E08-F03 ↔ E07.

## Audit and Traceability Tests
- Spend per-feature label preserved.

## Regression Risks
- Voice routing change inflating cost.

## Open Questions
- Per-coordinator finer-grained.
