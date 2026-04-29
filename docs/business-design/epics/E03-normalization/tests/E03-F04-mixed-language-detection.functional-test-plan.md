# E03-F04 — Mixed Language Detection: Functional Test Plan

## Scope
Verifies span detection precision, lang attribute on spans, and split-stitch
fallback for Google Hebrew TTS.

## Source User Stories
- S01 English spans tagged — Critical
- S02 Google split-and-stitch — High

## Test Scenarios
- **FT-112** "ערך p-value הוא 0.05" → spans [{he}, {en: p-value}, {he}, {num: 0.05}]. Critical.
- **FT-113** Single English letter inside Hebrew word treated as Hebrew. High.
- **FT-114** Brand name (e.g., `Microsoft Word`) tagged as English. High.
- **FT-115** Mixed sentence routed to Google → split + stitch ≤ 30 ms seam. High.
- **FT-116** Mixed sentence routed to Azure → inline `<lang>` honored. Critical.

## Negative Tests
- All-Hebrew sentence: no language switches emitted.
- All-English sentence: Hebrew voice falls back to English voice or fails clearly.

## Boundary Tests
- 1 character span; entire sentence English.

## Permission and Role Tests
- N/A.

## Integration Tests
- E03-F04 ↔ E07-F01 (Google) ↔ E07-F03 (Azure).

## Audit and Traceability Tests
- Per-span lang stored.

## Regression Risks
- Detector mistakes Latin transliteration for English; fix via bench.

## Open Questions
- Math span overlap with lang spans.
