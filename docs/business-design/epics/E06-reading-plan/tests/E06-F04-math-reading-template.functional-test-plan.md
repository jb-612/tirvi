# E06-F04 — Math Reading Template: Functional Test Plan

## Scope
Verifies math SSML grouping, variable pronunciation, breaks around operators.

## Source User Stories
- S01 grouping breaks — Critical
- S02 variable pronunciation — High

## Test Scenarios
- **FT-184** "x² + 1 = y" emits operator breaks. Critical.
- **FT-185** Variable "x" → "אקס" pronunciation. High.
- **FT-186** Greek letter α → Hebrew "אלפא". High.
- **FT-187** Long expression: break budget scaled. Medium.

## Negative Tests
- Garbled math fragment; fallback per E03-F05.

## Boundary Tests
- Single symbol; 50-symbol expression.

## Permission and Role Tests
- N/A.

## Integration Tests
- E03-F05 ↔ E06-F04 ↔ E07.

## Audit and Traceability Tests
- Template version stamped.

## Regression Risks
- New symbol uncovered.

## Open Questions
- Vector / matrix.
