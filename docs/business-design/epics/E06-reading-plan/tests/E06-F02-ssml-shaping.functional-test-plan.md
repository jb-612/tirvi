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
