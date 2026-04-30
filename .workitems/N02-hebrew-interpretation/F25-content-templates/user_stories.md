<!-- COMBINED from 3 biz sources @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->
<!-- - docs/business-design/epics/E03-normalization/stories/E03-F05-math-template.stories.md -->
<!-- - docs/business-design/epics/E06-reading-plan/stories/E06-F04-math-reading-template.stories.md -->
<!-- - docs/business-design/epics/E06-reading-plan/stories/E06-F05-table-reading-template.stories.md -->

# F25 — Content Templates (math + table reading)

## ─── from E03-F05-math-template ───

# E03-F05 — Math Expression Detection & Hebrew Math Template

## Source Basis
- PRD: §6.3 (math route)
- HLD: §5.2 (math SSML template)
- Research: src-003 §2.4 (no Hebrew-specific math lib; templating approach)
- Assumptions: math reading templates are Hebrew-localized rules in MVP

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student studying math | hears equations correctly | "x squared" → "x בריבוע" | template per pattern |
| P08 Backend Dev | implements templates | LaTeX-light vs plain notation | structured detection |
| P02 Coordinator | math Bagrut prep | range / variable conventions | covered patterns list |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: lexicon maintainer (math-symbol vocabulary).
3. System actors: math detector (E02-F04), reading-plan generator.
4. Approvals: template additions hit bench math pages.
5. Handoff: spoken-math output into SSML.
6. Failure recovery: unknown math symbol → spell with letter names + flag.

## Behavioural Model
- Hesitation: dev unsure how to handle vector / matrix notation.
- Rework: template over-emphasizes operator pauses.
- Partial info: complex equation; partial template; user feedback corrects.
- Retry: template revision lands monthly.

---

## User Stories

### Story 1: Common math patterns read in Hebrew

**As a** student
**I want** common math patterns (squared, square root, fraction, equality) read in Hebrew
**So that** I can follow algebra problems by ear.

#### Main Flow
1. Math detector tags patterns: `x²` → "x בריבוע"; `√x` → "שורש x"; `a/b` → "a חלקי b"; `=` → "שווה".
2. Template emits structured Hebrew with appropriate pauses.

#### Edge Cases
- Variables vs constants ambiguous; template treats single letter as variable.
- Mixed Hebrew+math sentence ("x גדול מ-5"); seamless integration.

#### Acceptance Criteria
```gherkin
Given a math expression "x² + 1 = y"
When normalization runs
Then the spoken form is "x בריבוע ועוד 1 שווה y"
```

#### Data and Business Objects
- `MathTemplateRule` (pattern, hebrew_template).

#### Dependencies
- DEP-INT to E02-F04 (math region detection), E06 (SSML).

#### Non-Functional Considerations
- Quality: pattern precision ≥ 90% on math bench pages.

#### Open Questions
- Vector / matrix notation in v1.1?

---

### Story 2: Unknown math symbol falls back to letter names

**As a** student
**I want** unknown symbols spelled out so I can recognize them
**So that** I'm not silently misled.

#### Main Flow
1. Template falls back to: spell symbol by Unicode letter or "סימן" placeholder.
2. SRE alert raised on novel symbols (above N occurrences).

#### Edge Cases
- Greek letters (α, β); hand-curated Hebrew names.
- LaTeX leftover (`\frac`); detector strips before template.

#### Acceptance Criteria
```gherkin
Given an unrecognized symbol "⊕" appears
When normalization runs
Then the spoken form includes "סימן מיוחד"
And SRE log records new symbol for backlog
```

#### Dependencies
- DEP-INT to E11-F05 (feedback path).

#### Non-Functional Considerations
- Reliability: never silently drop a symbol.

#### Open Questions
- MathSpeak Hebrew localization joint with HUJI (research §11)?

## ─── from E06-F04-math-reading-template ───

# E06-F04 — Math Reading Template (Plan Layer)

## Source Basis
- HLD: §5.2 reading plan
- Research: src-003 §2.4 (Hebrew math templating)
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student studying math | hears equation correctly | flat read | math template |
| P08 Backend Dev | implements template | symbol density | structured rendering |
| P02 Coordinator | math practice | numeric domain | template coverage |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: lexicon maintainer (Hebrew math vocabulary).
3. System actors: math region detector (E02-F04), normalization template (E03-F05).
4. Approvals: template changes hit math bench.
5. Handoff: SSML output to TTS.
6. Failure recovery: unknown symbol → fallback per E03-F05.

## Behavioural Model
- Hesitation: dev unsure how strict to be on grouping.
- Rework: numerator-denominator order.
- Partial info: chemistry symbols look similar; need bench fixtures.
- Retry: feedback drives improvements.

---

## User Stories

### Story 1: Equations rendered with grouping pauses

**As a** student
**I want** "x² + 1 = y" rendered with brief pauses around operators
**So that** I can parse the structure aurally.

#### Main Flow
1. Template emits `<say-as interpret-as="characters">` for variable letters.
2. Inserts `<break time="200ms"/>` around binary operators.

#### Edge Cases
- Long expression: inserted breaks scaled to length budget.

#### Acceptance Criteria
```gherkin
Given equation "x² + 1 = y"
When SSML is generated
Then breaks bracket "+", "=" operators
And output passes math-bench acceptance
```

#### Dependencies
- DEP-INT to E03-F05 (template rules), E07.

#### Non-Functional Considerations
- Quality: math read MOS gate.

---

### Story 2: Variable vs constant pronunciation distinction

**As a** dev
**I want** single Latin letters in math context pronounced as variable names ("x" → "אקס")
**So that** reading is unambiguous.

#### Main Flow
1. In math region, single Latin letters → Hebrew variable name.
2. Outside math (e.g., English text), Latin letter spelled per language span (E03-F04).

#### Edge Cases
- Greek letter in math; treat as variable with Hebrew name.

#### Acceptance Criteria
```gherkin
Given math region containing "x"
When SSML is generated
Then the Hebrew template emits variable pronunciation
```

#### Dependencies
- DEP-INT to E03-F04, E03-F05.

#### Non-Functional Considerations
- Quality: MOS gate.

#### Open Questions
- Vector / matrix template?

## ─── from E06-F05-table-reading-template ───

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
