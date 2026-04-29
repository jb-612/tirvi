# E08-F03 — Audio Cache: Functional Test Plan

## Scope
Verifies cache hit/miss, hash inclusion, hit-rate metric, lifecycle exemption.

## Source User Stories
- S01 cache by block_hash — Critical
- S02 hit-rate metric — High

## Test Scenarios
- **FT-223** Same SSML + voice → cache hit. Critical.
- **FT-224** Different voice → different key, different audio. Critical.
- **FT-225** Hash version bump → new key on objects. High.
- **FT-226** No lifecycle rule on `audio/`. Critical.
- **FT-227** Hit rate metric across hours. High.
- **FT-228** PUT retry on transient errors. Medium.

## Negative Tests
- Hash collision (synthetic) → wrong audio risk; voice-spec inclusion mitigates.
- GCS PUT permission missing; typed error.

## Boundary Tests
- 1-byte audio (impossible); 50 MB audio.

## Permission and Role Tests
- Bucket SA writes to `audio/` only via worker.

## Integration Tests
- E07 ↔ E08-F03 ↔ E11-F01 (lifecycle).

## Audit and Traceability Tests
- Hash version stamped.

## Regression Risks
- Voice rotation cache-miss flood.

## Open Questions
- Orphan eviction.
