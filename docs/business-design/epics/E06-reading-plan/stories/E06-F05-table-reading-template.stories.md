# E06-F05 — Table Reading Template (Row by Row)

## Source Basis
- PRD: §5 Use case 6 (read a table)
- HLD: §5.2 (table region template)
- Research: src-003 §2.4 (no Hebrew lib for math tables; Hebrew templating required)
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears table by row | flat read = nonsense | row-by-row template |
| P08 Backend Dev | builds template | merged cells | resilient rendering |
| P02 Coordinator | data tables | column header context | header repeats |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: lexicon maintainer (Hebrew table phrases).
3. System actors: block detector (E02-F04 table region).
4. Approvals: template change via review.
5. Handoff: SSML output.
6. Failure recovery: unknown table structure → fallback to plain row read.

## Behavioural Model
- Hesitation: dev unsure how to handle merged cells.
- Rework: table too long; chunked.
- Partial info: header missing; default to "עמודה 1".
- Retry: feedback corrects.

---

## User Stories

### Story 1: Tables read row by row with column-header context

**As a** student
**I want** a table read as "row 1: column A is X, column B is Y"
**So that** I can follow tabular content aurally.

#### Main Flow
1. Detector emits table region with rows and column headers.
2. Template iterates rows; for each cell emits "header: value".
3. Inserts breaks between rows.

#### Edge Cases
- Table without headers (data-only): generic "column 1, 2, …".
- Cell with multi-line text: read as one cell.

#### Acceptance Criteria
```gherkin
Given a 2×3 table with headers
When SSML is generated
Then output reads "row 1: <h1>: <c11>, <h2>: <c12>, <h3>: <c13>" with row breaks
```

#### Dependencies
- DEP-INT to E02-F04 table region, E07.

#### Non-Functional Considerations
- Accessibility: table read should be skippable per row.

---

### Story 2: Merged cells handled gracefully

**As a** student
**I want** merged cells read with a clarifying phrase
**So that** I understand the structure.

#### Main Flow
1. Detector flags merged cells.
2. Template adds "merged across columns N..M" phrase.

#### Edge Cases
- Diagonal merges (rare); fallback to flat.

#### Acceptance Criteria
```gherkin
Given a row with a cell merged across 2 columns
When the template runs
Then SSML includes "across 2 columns" clarifier
```

#### Dependencies
- DEP-INT to E02-F04.

#### Non-Functional Considerations
- Quality: bench passes with merged-cell page.

#### Open Questions
- Per-domain template variants (financial table vs math truth table)?
