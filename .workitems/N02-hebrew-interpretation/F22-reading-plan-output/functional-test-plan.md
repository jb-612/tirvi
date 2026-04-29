<!-- DERIVED FROM docs/business-design/epics/E06-reading-plan/tests/E06-F01-block-typed-reading-plan.functional-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:58:03Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E06-F01 — Reading Plan: Functional Test Plan

## Scope
Verifies plan.json schema, invariants, and generation across block types.

## Source User Stories
- S01 SSML + tokens — Critical
- S02 invariants — Critical

## Test Scenarios
- **FT-168** Plan emitted per page; schema valid. Critical.
- **FT-169** Block IDs unique; tokens belong to blocks. Critical.
- **FT-170** SSML well-formed XML. Critical.
- **FT-171** Per-token provenance present. High.
- **FT-172** Empty figure-caption block skipped from TTS. Medium.
- **FT-173** Long pages (50+ blocks) plan emitted. High.

## Negative Tests
- Adapter returns malformed plan; validator rejects.

## Boundary Tests
- 1 block; 200 blocks.

## Permission and Role Tests
- N/A.

## Integration Tests
- E06 ↔ E04, E05, E07, E09.

## Audit and Traceability Tests
- Per-token provenance per stage.

## Regression Risks
- Schema bump without consumer update.

## Open Questions
- Plan size cap.
