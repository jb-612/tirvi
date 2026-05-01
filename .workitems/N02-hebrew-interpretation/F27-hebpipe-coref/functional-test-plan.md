<!-- DERIVED FROM docs/business-design/epics/E04-nlp-disambiguation/tests/E04-F04-hebpipe-coref.functional-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E04-F04 — HebPipe Coref: Functional Test Plan

## Scope
Verifies optional coref enrichment is correct when enabled.

## Source User Stories
- S01 opt-in run — High
- S02 quality lift — High

## Test Scenarios
- **FT-141** Long page (≥ 500 words) → HebPipe runs. High.
- **FT-142** Short page → HebPipe skipped. High.
- **FT-143** Coref chain points to correct antecedent on bench. High.
- **FT-144** Disabled flag → coref never runs. Critical.
- **FT-145** Coref output absent → reading plan ignores gracefully. High.

## Negative Tests
- HebPipe crash → silent fallback.

## Boundary Tests
- Edge case at threshold word count.

## Permission and Role Tests
- N/A.

## Integration Tests
- E04-F04 ↔ E06 reading plan (gender / number agreement).

## Audit and Traceability Tests
- Per-page coref flag in manifest.

## Regression Risks
- HebPipe upgrade altering chain format.

## Open Questions
- MVP or v1.1?
