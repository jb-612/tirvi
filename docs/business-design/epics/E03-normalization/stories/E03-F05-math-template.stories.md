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
