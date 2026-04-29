# E11-F01 — 24h TTL: Functional Test Plan

## Scope
Verifies lifecycle config, opt-in 7-day flow, drift detector.

## Source User Stories
- S01 lifecycle on confidential prefixes — Critical
- S02 opt-in 7-day with consent — High

## Test Scenarios
- **FT-292** Lifecycle drift detected daily. Critical.
- **FT-293** Opt-in 7-day for adult preserves doc. High.
- **FT-294** Minor opt-in triggers parent consent. Critical.
- **FT-295** Opt-in expiration auto-revert. High.
- **FT-296** Audio cache exempt. Critical.

## Negative Tests
- Lifecycle disabled manually; drift catches.

## Boundary Tests
- 24h ± 1h tolerance; 7d ± 1h tolerance.

## Permission and Role Tests
- Lifecycle SA only.

## Integration Tests
- E01-F05 ↔ E11-F01 ↔ E11-F02.

## Audit and Traceability Tests
- Lifecycle action audit.

## Regression Risks
- New prefix without lifecycle.

## Open Questions
- Audio cache exemption legality.
