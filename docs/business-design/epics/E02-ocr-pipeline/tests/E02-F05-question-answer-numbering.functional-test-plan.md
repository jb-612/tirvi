# E02-F05 — Question/Answer Numbering: Functional Test Plan

## Scope
Verifies numbering schemes (Arabic, Hebrew letters, Hebrew ordinals, Latin)
canonicalize correctly and answers anchor to their parent question.

## Source User Stories
- E02-F05-S01 normalized identifiers — Critical
- E02-F05-S02 answer-to-question anchoring — Critical

## Functional Objects Under Test
- Number tagger
- `Block.question_no`, `Block.option_no`, `Block.parent_question_no`

## Test Scenarios
- **FT-081** `שאלה 1..3` → question_no=1..3. Critical.
- **FT-082** `1. 2. 3.` → question_no=1..3. Critical.
- **FT-083** `א ב ג ד` → option_no="א".."ד". Critical.
- **FT-084** Mixed scheme on one page (rare): tagger normalizes per block. High.
- **FT-085** Answer-to-question anchor within vertical threshold. Critical.
- **FT-086** Sub-question (4a, 4b) → "4.1", "4.2". High.
- **FT-087** "see question 4" mid-paragraph not tagged. Medium.

## Negative Tests
- Orphan answer (no preceding stem): `parent_question_no=null`; manifest flags.
- Numbering pattern unknown: position-based fallback.

## Boundary Tests
- 1-question page; 50-question practice page.

## Permission and Role Tests
- N/A.

## Integration Tests
- Numbering ↔ E06 reading plan template; ↔ E09 player navigation.

## Audit and Traceability Tests
- Tagger emits per-block numbering confidence.

## Regression Risks
- Hierarchy encoding ambiguity; ADR.

## Open Questions
- Hierarchical encoding choice.
