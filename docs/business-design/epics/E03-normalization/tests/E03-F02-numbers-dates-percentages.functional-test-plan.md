# E03-F02 — Numbers/Dates/Percentages: Functional Test Plan

## Scope
Verifies Hebrew number expansion (cardinal, ordinal, gendered), date/time
formats, percentage, range, fraction.

## Source User Stories
- S01 numbers natural — Critical
- S02 ranges/fractions/percentages — Critical

## Test Scenarios
- **FT-099** 247 → "מאתיים ארבעים ושבע[ה]". Critical.
- **FT-100** Year 2026 → "שנת אלפיים עשרים ושש". High.
- **FT-101** Ordinal #3 → "השלישי". High.
- **FT-102** Range 1-5 → "מ-1 עד 5". Critical.
- **FT-103** Fraction 1/4 → "רבע". High.
- **FT-104** 99.9% → "תשעים ותשע נקודה תשע אחוז". Critical.
- **FT-105** Phone-number context → digit-by-digit. Medium.

## Negative Tests
- Date 13/13/2026: detector flags invalid; reads digit-by-digit.
- Percentage > 100 (e.g., 150%): pronounced normally.

## Boundary Tests
- 0, 1, 2 (gender/grammar singular forms).
- Very large numbers (millions, billions).

## Permission and Role Tests
- N/A.

## Integration Tests
- E03-F02 ↔ E04 (POS for gender) ↔ E06 (SSML emission).

## Audit and Traceability Tests
- Numeric rule per-token tag in audit log.

## Regression Risks
- num2words version bump shifting forms.

## Open Questions
- DD/MM vs MM/DD ambiguity guard.
