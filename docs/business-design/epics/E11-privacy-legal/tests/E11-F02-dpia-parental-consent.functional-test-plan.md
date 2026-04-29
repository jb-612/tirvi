# E11-F02 — DPIA + Consent: Functional Test Plan

## Scope
Verifies consent flow, DPIA artifact, revocation cascade.

## Source User Stories
- S01 DPIA + consent — Critical
- S02 revocation — Critical

## Test Scenarios
- **FT-297** Self-declared minor → parent flow. Critical.
- **FT-298** ConsentRecord persisted. Critical.
- **FT-299** Revocation triggers cascade within 30 min. Critical.
- **FT-300** DPIA artifact published in repo. High.
- **FT-301** Consent UI minimum-PII. Critical.

## Negative Tests
- Parent declines; upload denied.
- Consent token forged; rejected.

## Boundary Tests
- Age 14; age 13 (refusal); age 18 (no consent needed).

## Permission and Role Tests
- ConsentRecord readable only by SRE / legal.

## Integration Tests
- E11-F02 ↔ E01-F01 (gate), E01-F04 (cascade).

## Audit and Traceability Tests
- Per-consent timestamp + parent identifier (encrypted).

## Regression Risks
- Consent text changes; new versions logged.

## Open Questions
- Age threshold definition.
