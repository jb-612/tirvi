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
