<!-- DERIVED FROM docs/business-design/epics/E05-pronunciation/tests/E05-F03-homograph-lexicon.functional-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E05-F03 — Homograph Lexicon: Functional Test Plan

## Scope
Verifies override loader and bench coverage report.

## Source User Stories
- S01 top-500 override — Critical
- S02 coverage tracked — High

## Test Scenarios
- **FT-158** Lexicon entry overrides Nakdan output. Critical.
- **FT-159** Entry without POS filter applies broadly. High.
- **FT-160** Conflict warns. High.
- **FT-161** Per-entry contribution report. High.
- **FT-162** Lexicon load ≤ 200 ms. Medium.

## Negative Tests
- Malformed YAML rejected.

## Boundary Tests
- Empty / 5000-entry lexicon.

## Permission and Role Tests
- Read-only at runtime.

## Integration Tests
- E05-F01 override layer.

## Audit and Traceability Tests
- Per-token override stamped with lexicon version.

## Regression Risks
- Removing entry causing regression; PR review checks bench.

## Open Questions
- Per-domain split.
