# E07-F03 — Azure Adapter: Functional Test Plan

## Scope
Verifies SSML w/ bookmark + WordBoundary events, mixed-language path, swap-in.

## Source User Stories
- S01 Hebrew + WordBoundary — Critical
- S02 Wavenet outage swap-in — High

## Test Scenarios
- **FT-203** SSML + `<bookmark>` → per-word timing. Critical.
- **FT-204** Mixed Hebrew/English → both langs covered. Critical.
- **FT-205** Wavenet failure threshold → routing to Azure. High.
- **FT-206** Cache hit per-voice. Critical.
- **FT-207** Voice deprecation handled with ADR-001 update. Medium.

## Negative Tests
- Azure outage; reroute back to Wavenet.

## Boundary Tests
- Single bookmark; 5000-bookmark block.

## Permission and Role Tests
- Azure key in Secret Manager; runtime SA only.

## Integration Tests
- E03-F04 ↔ E06-F03 ↔ E07-F03 ↔ E08-F01.

## Audit and Traceability Tests
- Per-block voice + provider stamped.

## Regression Risks
- SDK upgrade event API changes.

## Open Questions
- Default voice (Hila vs Avri).
