# E10-F02 — Quality Gates CI: Functional Test Plan

## Scope
Verifies per-stage gates run, fail on regression, dashboard presence.

## Source User Stories
- S01 gate failures — Critical
- S02 dashboard — High

## Test Scenarios
- **FT-270** OCR WER regression > 0.5% blocks PR. Critical.
- **FT-271** NLP UD-Hebrew accuracy drops blocks PR. Critical.
- **FT-272** Diacritization accuracy drop blocks. Critical.
- **FT-273** Stress accuracy drop blocks. High.
- **FT-274** TTS MOS drop blocks. Critical.
- **FT-275** Dashboard shows trends. High.

## Negative Tests
- Bench infrastructure outage; CI warns; emergency waiver.

## Boundary Tests
- Threshold edges.

## Permission and Role Tests
- Threshold change via ADR-only PR.

## Integration Tests
- E10-F02 ↔ E02-F06, E04, E05, E07, E10-F01, E10-F03.

## Audit and Traceability Tests
- Per-PR result archived.

## Regression Risks
- Bench drift; quarterly rotation.

## Open Questions
- Per-stage threshold table source of truth.
