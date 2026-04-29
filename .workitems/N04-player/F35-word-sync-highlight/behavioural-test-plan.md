<!-- DERIVED FROM docs/business-design/epics/E09-player-ui/tests/E09-F03-word-sync-highlight.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:09:31Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E09-F03 — Word-Sync Highlight: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student preference | P01 | distraction | toggle intensity |
| Reduced motion | P01 | overwhelm | OS pref honored |
| Performance jank | P09 | drops | budget |

## Scenarios
- **BT-165** Student finds highlight too bold; toggles soft mode.
- **BT-166** OS prefers reduced motion; subtle highlight only.
- **BT-167** Long block; animation stays smooth on mid laptop.

## Edge / Misuse / Recovery
- Edge: high-DPI Retina; CSS pixels stable.
- Misuse: dev disables animation entirely; a11y still serves.
- Recovery: timing missing → block-level highlight.

## Open Questions
- Soft / bold toggle in MVP.
