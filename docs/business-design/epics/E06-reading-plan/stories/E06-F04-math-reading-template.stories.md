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
