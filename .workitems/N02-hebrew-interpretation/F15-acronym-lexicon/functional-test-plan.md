<!-- DERIVED FROM docs/business-design/epics/E03-normalization/tests/E03-F03-acronym-lexicon.functional-test-plan.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E03-F03 — Acronym Lexicon: Functional Test Plan

## Scope
Verifies lexicon load, deterministic tagging, fallback behaviour, feedback
cycle.

## Source User Stories
- S01 common acronyms — Critical
- S02 unknown fallback — Critical

## Test Scenarios
- **FT-106** ד״ר → דוקטור. Critical.
- **FT-107** עמ׳ → עמוד. Critical.
- **FT-108** ת״א ambiguity → context picks. High.
- **FT-109** Acronym at sentence end with `?` → tagger preserves punctuation. High.
- **FT-110** Unknown acronym → letter-by-letter SSML. Critical.
- **FT-111** Lexicon version stamped on output. Medium.

## Negative Tests
- Lexicon file corrupt; loader fails fast.
- Acronym embedded in URL; left untouched.

## Boundary Tests
- Empty lexicon: every acronym falls back.
- 5000-entry lexicon: load < 200 ms.

## Permission and Role Tests
- Lexicon is read-only at runtime; updates via PR only.

## Integration Tests
- E03-F03 ↔ E04 NLP (token boundary) ↔ E06 SSML.

## Audit and Traceability Tests
- Per-token expansion logged with lexicon version.

## Regression Risks
- Removing an entry without notifying QA.

## Open Questions
- Domain-specific disambiguation gating.
