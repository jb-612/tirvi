# E04-F02 — AlephBERT/YAP Fallback: Functional Test Plan

## Scope
Verifies fallback selection, schema mapping, and recovery to primary.

## Source User Stories
- S01 fallback triggers — Critical
- S02 schema mapping — High

## Test Scenarios
- **FT-131** 3 retries fail → fallback used; `provider="alephbert+yap"`. Critical.
- **FT-132** Subsequent pages use primary if it recovers. High.
- **FT-133** AlephBERT POS labels mapped to canonical enum. Critical.
- **FT-134** Missing fields filled with `null`. Medium.
- **FT-135** Both adapters fail → degraded result with flag. High.

## Negative Tests
- Fallback also down → typed error; reading plan emits flat hints.

## Boundary Tests
- Single fallback invocation; many in burst.

## Permission and Role Tests
- N/A.

## Integration Tests
- E04-F02 ↔ E04-F01 ↔ E10-F05 (telemetry).

## Audit and Traceability Tests
- Provider per token + page logged.

## Regression Risks
- AlephBERT POS schema change unmapped.

## Open Questions
- Run shadow during MVP for parity comparison?
