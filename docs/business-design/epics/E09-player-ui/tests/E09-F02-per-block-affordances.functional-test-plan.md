# E09-F02 — Per-Block Affordances: Functional Test Plan

## Scope
Verifies per-block buttons (question-only, answers-only), keyboard, ARIA.

## Source User Stories
- S01 question only — Critical
- S02 answers only — Critical

## Test Scenarios
- **FT-239** Click "play question 5" → only Q5 plays. Critical.
- **FT-240** Click "play answers" → 4 answers in sequence with breaks. Critical.
- **FT-241** Audio not ready → "preparing" disabled state. High.
- **FT-242** Keyboard equivalent (Enter / Space). Critical.
- **FT-243** ARIA labels present. Critical.

## Negative Tests
- Missing block_id; no affordance rendered.

## Boundary Tests
- Single question per page; 30 questions per page.

## Permission and Role Tests
- N/A.

## Integration Tests
- E02-F05 ↔ E06-F02 ↔ E08 ↔ E09-F02.

## Audit and Traceability Tests
- Per-button click logged anonymized.

## Regression Risks
- Block ordering change breaks affordances.

## Open Questions
- Long-press alternative on touch.
