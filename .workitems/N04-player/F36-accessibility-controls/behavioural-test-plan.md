<!-- DERIVED FROM docs/business-design/epics/E09-player-ui/tests/E09-F04-controls.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:12:29Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E09-F04 — Controls: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student tunes pace | P01 | over-correction | sensible defaults |
| Discoverability | P01 | features hidden | tooltips + tutorial |
| Coordinator presets | P02 | mismatched preferences | per-session |

## Scenarios
- **BT-168** Student lowers speed in dense passage.
- **BT-169** Student rage-presses repeat; rate-limit.
- **BT-170** Coordinator sets defaults for class demo.
- **BT-171** Student toggles high-contrast at night.

## Edge / Misuse / Recovery
- Edge: speed at extremes; pitch artifacts.
- Misuse: dev script set speed to 5×; clamped.
- Recovery: revert to defaults via single button.

## Open Questions
- Persist preferences in localStorage.
