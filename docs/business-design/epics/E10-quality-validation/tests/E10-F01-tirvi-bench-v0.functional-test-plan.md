# E10-F01 — tirvi-bench v0: Functional Test Plan

## Scope
Verifies bench fixtures, ground truth, annotation tooling.

## Source User Stories
- S01 20-page held-out — Critical
- S02 annotation tooling — High

## Test Scenarios
- **FT-265** 8 digital + 8 scanned + 4 handwriting (deferred). Critical.
- **FT-266** Each page has text + blocks + IPA truth. Critical.
- **FT-267** Provenance per page recorded. Critical.
- **FT-268** Annotator CLI roundtrip stable. High.
- **FT-269** Truth update bumps version + invalidates baselines. High.

## Negative Tests
- Page from publisher (copyrighted) flagged for replacement.

## Boundary Tests
- Edge bench page for each layer (math, civics, mixed-language).

## Permission and Role Tests
- Truth files write-protected; PRs only.

## Integration Tests
- Bench ↔ E02-F06, E10-F02, E10-F03.

## Audit and Traceability Tests
- Versioned releases.

## Regression Risks
- Provenance violations.

## Open Questions
- Public release scope.
