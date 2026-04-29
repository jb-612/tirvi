# E10-F03 — MOS Study: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Participant fatigue | P05 | bias | sample limit |
| Orchestrator drift | P12 | non-repro | versioned protocol |
| Parent consent | P03 | refusal | gracious flow |

## Scenarios
- **BT-185** Participant takes break mid-session; resumes without bias.
- **BT-186** Orchestrator updates protocol; new version logged.
- **BT-187** Parent declines consent; participation cancelled.

## Edge / Misuse / Recovery
- Edge: low-volume audio device; bench acoustic profile.
- Misuse: participant rates without listening; outlier filter catches.
- Recovery: audit outliers; revoke if needed.

## Open Questions
- Cross-cultural representation.
