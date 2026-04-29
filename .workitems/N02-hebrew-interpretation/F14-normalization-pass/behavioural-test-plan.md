<!-- DERIVED FROM docs/business-design/epics/E03-normalization/tests/E03-F01-ocr-artifact-repair.behavioural-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:43:16Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E03-F01 — OCR Artifact Repair: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student finds repaired text odd | P01 | distrust | repair-diff visible if requested |
| Dev tunes rules | P08 | over-fit | bench |

## Scenarios
- **BT-063** Student sees repaired text; spots over-zealous merge; reports.
- **BT-064** Dev adds publisher-specific rule; bench shows lift.
- **BT-065** Coordinator scans publisher A; rule X applied; manifest annotates.
- **BT-066** SRE pulls repair-diff for stuck doc.

## Edge / Misuse / Recovery
- Edge: repair on 1-word page no-ops.
- Misuse: dev disables repair locally; CI enforces.
- Recovery: rule rolled back via PR after regression.

## Collaboration Breakdown
- Lexicon maintainer cannot reach dev; rule changes follow PR with bench.

## Open Questions
- Should student see "we cleaned this" affordance?
