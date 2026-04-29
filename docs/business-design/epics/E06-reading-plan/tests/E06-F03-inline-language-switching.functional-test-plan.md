# E06-F03 — Inline Lang Switching: Functional Test Plan

## Scope
Verifies Azure path inline `<lang>` and Google split-and-stitch fallback.

## Source User Stories
- S01 Azure inline — Critical
- S02 Google split-stitch — High

## Test Scenarios
- **FT-179** Azure adapter: inline `<lang xml:lang="en-US">` honored. Critical.
- **FT-180** Google adapter: split into Hebrew/English chunks. High.
- **FT-181** Stitched seam ≤ 30 ms perceived. High.
- **FT-182** Span boundary precision ≥ 95% on bench. High.
- **FT-183** Nested spans collapsed to outermost. Medium.

## Negative Tests
- Voice deprecates `<lang>` mid-cycle; profile catches and falls back.

## Boundary Tests
- Sentence with 1 single-letter English span; minimal switching.
- All-English sentence in Hebrew page; voice forced to en or fail clearly.

## Permission and Role Tests
- N/A.

## Integration Tests
- E03-F04 ↔ E06-F03 ↔ E07-F01/F03 ↔ E08-F01.

## Audit and Traceability Tests
- Per-span lang and voice route logged.

## Regression Risks
- Detector mistakes; bench guards.

## Open Questions
- Cross-fade vs gap-zero.
