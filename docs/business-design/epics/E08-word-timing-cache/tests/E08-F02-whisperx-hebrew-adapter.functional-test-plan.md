# E08-F02 — WhisperX: Functional Test Plan

## Scope
Verifies forced alignment quality, latency, telemetry.

## Source User Stories
- S01 align — Critical
- S02 telemetry — High

## Test Scenarios
- **FT-219** Per-block alignment p50 ≤ 80 ms. Critical.
- **FT-220** Latency ≤ 1 s per block on dev hardware. High.
- **FT-221** Failure → degraded result. High.
- **FT-222** Bench histogram emitted. High.

## Negative Tests
- Audio cuts mid-word; alignment best-effort.

## Boundary Tests
- 1-second audio; 60-second audio.

## Permission and Role Tests
- Hebrew acoustic model loaded only with `models` profile.

## Integration Tests
- E07 audio ↔ E08-F02 ↔ E09 player.

## Audit and Traceability Tests
- Alignment-error metric stored.

## Regression Risks
- Acoustic model upgrade.

## Open Questions
- WhisperX vs MFA.
