<!-- DERIVED FROM docs/business-design/epics/E06-reading-plan/tests/E06-F02-ssml-shaping.functional-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:00:38Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E06-F02 — SSML Shaping: Functional Test Plan

## Scope
Verifies per-block-type SSML profiles and provider-specific compatibility.

## Source User Stories
- S01 question slow + emphasis — Critical
- S02 answer pause — Critical

## Test Scenarios
- **FT-174** question_stem → `prosody rate="0.95"` + emphasis. Critical.
- **FT-175** answer_option → 700 ms break between options. Critical.
- **FT-176** Heading block → light emphasis. High.
- **FT-177** Long question splits with mid-block break. Medium.
- **FT-178** Voice without `<emphasis>` → alternate profile. High.

## Negative Tests
- Provider rejects SSML element; profile fallback.

## Boundary Tests
- Single-token block; very long block.

## Permission and Role Tests
- N/A.

## Integration Tests
- E06-F02 ↔ E07-F01..F03 voices.

## Audit and Traceability Tests
- Profile per voice version stamped.

## Regression Risks
- Voice family deprecates attribute.

## Open Questions
- Per-student pause customization.
