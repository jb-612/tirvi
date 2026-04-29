<!-- DERIVED FROM docs/business-design/epics/E02-ocr-pipeline/tests/E02-F04-block-segmentation.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:39:57Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E02-F04 — Block-Level Structural Detection: Behavioural Test Plan

## Behavioural Scope
Student behaviour when block tagging is wrong; dev behaviour when adding new
block types.

## Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| Wrong question grouping | P01 | "answers played as questions" | feedback signal |
| Detector tuning | P08 | over-fit | bench |
| Coordinator scans skewed | P02 | block boundaries warped | deskew |

## Scenarios
- **BT-051** Student hears answers when expecting question stem; "wrong block" flag visible.
- **BT-052** Coordinator scans skewed page; detector fails on column boundary; UI suggests rescan.
- **BT-053** Dev adds `math_region` heuristic; bench shows precision improvement.
- **BT-054** Adversarial page: instructions mid-question; detector merges into stem; user feedback flags.

## Edge / Misuse / Recovery
- Edge: nested table within a paragraph; detector keeps as table.
- Misuse: dev disables heuristic; CI gate blocks.
- Recovery: low-confidence block triggers `paragraph` default + audit.

## Collaboration Breakdown
- Coordinator reports systematic mistag for one exam series; dev adds bench page.

## Open Questions
- Should we expose block edits to coordinators (corrective UI)?
