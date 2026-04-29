# E07-F01 — Google Wavenet Adapter: Functional Test Plan

## Scope
Verifies SSML synthesis with `<mark>` timepoints, audio + timing emission,
cache integration, fallback when marks truncated.

## Source User Stories
- S01 audio + word marks — Critical
- S02 cache by block_hash — Critical

## Test Scenarios
- **FT-193** SSML with 30 marks → 30 timepoints. Critical.
- **FT-194** Marks truncated → manifest flag + alignment fallback. Critical.
- **FT-195** Cache hit returns audio without API call. Critical.
- **FT-196** Cache miss writes audio + timings. Critical.
- **FT-197** Rate limit → backoff retry succeeds. High.
- **FT-198** Audio codec MP3 by default. Medium.

## Negative Tests
- API auth fail; typed error.
- API quota exceeded; queued retry.

## Boundary Tests
- 1-word block; 1000-word block.

## Permission and Role Tests
- Adapter SA has TTS user role only.

## Integration Tests
- E07-F01 ↔ E08-F01/F02 ↔ E08-F03.

## Audit and Traceability Tests
- Per-block voice + provider stamped.

## Regression Risks
- Google deprecates Hebrew marks; ADR-001 refresh.

## Open Questions
- Voice variant choice.
