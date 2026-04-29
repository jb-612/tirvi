# E10-F03 — Blind MOS Study: Functional Test Plan

## Scope
Verifies study protocol, sample server, ratings aggregation.

## Source User Stories
- S01 panel of 10 — Critical
- S02 sample server — High

## Test Scenarios
- **FT-276** Per-voice MOS computed. Critical.
- **FT-277** Outlier sensitivity analysis. High.
- **FT-278** Sample server randomizes per participant. High.
- **FT-279** No PII captured. Critical.
- **FT-280** Ethics + parental consent recorded. Critical.

## Negative Tests
- Participant withdraws; ratings purged.
- Ratings invalid (e.g., all 1s); flagged.

## Boundary Tests
- Smaller (n=8) panel; MOS gate adjusted.
- Larger panel for v1.

## Permission and Role Tests
- Sample audio access controlled.

## Integration Tests
- MOS ↔ E07-F04 voice routing decisions.

## Audit and Traceability Tests
- Anonymized participant ID; ratings versioned.

## Regression Risks
- Voice version change requires re-rating.

## Open Questions
- Cross-cultural panel.
