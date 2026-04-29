# E11-F04 — No-PII Logging Audit: Functional Test Plan

## Scope
Verifies scrubber rules, quarterly audit, lint enforcement.

## Source User Stories
- S01 scrubber — Critical
- S02 quarterly audit — High

## Test Scenarios
- **FT-307** Scrubber drops document content fields. Critical.
- **FT-308** Quarterly audit pipeline runs. High.
- **FT-309** Lint catches `log.info(text)` with content variable. Critical.
- **FT-310** Suspicious pattern detection alerts. High.

## Negative Tests
- New field type without scrub rule; default-deny.

## Boundary Tests
- Edge: hashed fields meet "non-PII" definition.

## Permission and Role Tests
- Audit pipeline SA-only.

## Integration Tests
- All stages ↔ scrubber.

## Audit and Traceability Tests
- Quarterly results stored ≥ 1 year.

## Regression Risks
- New stage added without scrubber discipline.

## Open Questions
- Hash vs drop policy.
