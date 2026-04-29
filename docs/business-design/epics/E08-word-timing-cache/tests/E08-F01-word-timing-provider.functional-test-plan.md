# E08-F01 — WordTimingProvider: Functional Test Plan

## Scope
Verifies adapter selection, source field, fallback budget, telemetry.

## Source User Stories
- S01 source switching — Critical
- S02 telemetry — High

## Test Scenarios
- **FT-213** Wavenet full marks → source=tts-marks. Critical.
- **FT-214** Chirp no marks → source=forced-alignment. Critical.
- **FT-215** Truncated marks → fallback. Critical.
- **FT-216** Failover ≤ 200 ms. High.
- **FT-217** Both fail → degraded result. High.
- **FT-218** Per-source counter emitted. High.

## Negative Tests
- Empty audio → typed error.

## Boundary Tests
- 1-word block; 1000-word block.

## Permission and Role Tests
- N/A.

## Integration Tests
- E08-F01 ↔ E07 + E08-F02 + E09.

## Audit and Traceability Tests
- Per-block timing source stamped.

## Regression Risks
- Voice change without cache invalidation.

## Open Questions
- Auto vs explicit policy.
