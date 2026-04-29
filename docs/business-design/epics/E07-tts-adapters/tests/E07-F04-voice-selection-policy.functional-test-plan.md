# E07-F04 — Voice Selection Policy: Functional Test Plan

## Scope
Verifies per-block routing logic, failover policy, observability.

## Source User Stories
- S01 routing by use case — Critical
- S02 failover — Critical

## Test Scenarios
- **FT-208** Continuous mode → Chirp. Critical.
- **FT-209** Word-sync mode → Wavenet (default). Critical.
- **FT-210** Failure-rate threshold → swap-in. Critical.
- **FT-211** Routing decision logged with reason. High.
- **FT-212** Cooldown before re-promote. Medium.

## Negative Tests
- Both providers down; manifest flag.

## Boundary Tests
- Threshold exact; threshold + 1.

## Permission and Role Tests
- Routing config writable only by SRE.

## Integration Tests
- E07-F04 ↔ E07-F01..F03.

## Audit and Traceability Tests
- Decision audit log.

## Regression Risks
- Threshold tuning; bench.

## Open Questions
- Cooldown duration default.
