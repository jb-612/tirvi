# E05-F04 — Confidence Scoring: Functional Test Plan

## Scope
Verifies aggregation, threshold tuning, alerting.

## Source User Stories
- S01 aggregator — Critical
- S02 SRE alert — High

## Test Scenarios
- **FT-163** Aggregator computes weighted average. Critical.
- **FT-164** Lexicon override fixes confidence to 1.0. Critical.
- **FT-165** Missing stage → null excluded. Medium.
- **FT-166** Low-confidence rate ≥ 10% over 30 min triggers alert. High.
- **FT-167** Threshold tuning preserves output stability. Medium.

## Negative Tests
- Confidence aggregation missing inputs; null result with reason.
- Spurious alert: dedup window.

## Boundary Tests
- All-1.0 confidence; all-low.

## Permission and Role Tests
- N/A.

## Integration Tests
- E04 + E05-F01 + F02 + F03 → aggregator → telemetry.

## Audit and Traceability Tests
- Aggregation weights versioned.

## Regression Risks
- Threshold change → noise.

## Open Questions
- Surface in UI?
