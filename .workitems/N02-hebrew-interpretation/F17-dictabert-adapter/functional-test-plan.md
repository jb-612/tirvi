<!-- DERIVED FROM docs/business-design/epics/E04-nlp-disambiguation/tests/E04-F01-dictabert-adapter.functional-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T20:46:18Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E04-F01 — DictaBERT Adapter: Functional Test Plan

## Scope
Verifies primary NLP path on Hebrew text including segmentation, POS, lemma,
morphological features.

## Source User Stories
- S01 segmentation/POS/lemma/morph — Critical
- S02 disambiguation — Critical

## Test Scenarios
- **FT-124** Sample sentence → per-token POS, lemma, morph. Critical.
- **FT-125** Per-page latency ≤ 3 s on dev hardware. Critical.
- **FT-126** Compound prefix (`כשהתלמיד`) segmented. Critical.
- **FT-127** Homograph (`ספר` verb vs noun) disambiguated by context. Critical.
- **FT-128** Confidence margin emitted; ambiguous tokens flagged. High.
- **FT-129** UD-Hebrew accuracy ≥ 92% on bench. Critical.
- **FT-130** Empty text → empty result; no crash. Medium.

## Negative Tests
- Model service down: 3 retries → fallback path triggered.
- Garbage input: result emitted with warnings.

## Boundary Tests
- 1-token; 5000-token page.

## Permission and Role Tests
- Model service callable only from worker SA.

## Integration Tests
- E04-F01 ↔ E03 input ↔ E05 diacritization ↔ E06 reading plan.

## Audit and Traceability Tests
- Per-token confidence; provider stamp.

## Regression Risks
- Model version bump shifting POS labels; mapper guards.

## Open Questions
- Pre-segmentation needed?
