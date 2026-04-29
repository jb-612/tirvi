# E08-F03 — Audio Cache: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student re-listens | P01 | unnoticed cost saving | metric |
| Coordinator bulk | P02 | high reuse | hit-rate |
| SRE budget | P04 | spike from rotation | dashboard |

## Scenarios
- **BT-152** Student replays sentence 5×; no API calls.
- **BT-153** Coordinator uploads 3 variants; sentence-level cache (E08-F04) helps.
- **BT-154** Voice rotation; SRE sees expected cache-miss spike.

## Edge / Misuse / Recovery
- Edge: byte-level corruption; evict + re-synthesize.
- Misuse: dev clears cache to test; reset metric counter.
- Recovery: warm-up plan on rotation.

## Open Questions
- Orphan eviction default.
