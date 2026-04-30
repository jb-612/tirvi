<!-- COMBINED from 3 biz sources @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-30T17:52:50Z -->

## ─── from E03-F05-math-template ───

# E03-F05 — Math Template: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student hears equation | P01 | misread | bench |
| Coordinator math practice | P02 | wide pattern set | rule library |
| Dev adds template | P08 | over-fit | bench |

## Scenarios
- **BT-079** Student studying linear algebra; vector notation falls back; recognized clearly.
- **BT-080** Coordinator uses 8 math practice exams; bench reflects coverage.
- **BT-081** Dev adds geometry symbols; bench validates lift.
- **BT-082** Adversarial expression with deeply nested fraction; templates avoid stack-overflow.

## Edge / Misuse / Recovery
- Edge: chemistry-only page mistagged as math; bench catches.
- Misuse: dev hard-codes pattern; lint enforces template-driven.
- Recovery: missing template → fallback symbol log triggers backlog.

## Collaboration Breakdown
- Lexicon maintainer & math educator pair; documented contact.

## Open Questions
- Vector / matrix in v1.1?

## ─── from E06-F04-math-reading-template ───

# E06-F04 — Math Reading Template: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student studying math | P01 | misread | bench MOS |
| Coordinator math practice | P02 | wide patterns | rule library |

## Scenarios
- **BT-125** Student parses equation aurally; passes recognition test.
- **BT-126** Coordinator uploads diverse math practice; bench expands.
- **BT-127** Adversarial nested fraction; fallback graceful.

## Edge / Misuse / Recovery
- Edge: chemistry mistagged as math; bench page.
- Misuse: dev hard-codes pattern.
- Recovery: missing template logged.

## Open Questions
- HUJI MathSpeak partnership.

## ─── from E06-F05-table-reading-template ───

# E06-F05 — Table Template: Behavioural Test Plan

## Patterns Covered
| Behaviour | Persona | Risk | Test |
|-----------|---------|------|------|
| Student navigates tables | P01 | overwhelmed | per-row affordance |
| Coordinator data tables | P02 | uncovered domain | bench |
| Dev tunes phrasing | P08 | over-fit | bench |

## Scenarios
- **BT-128** Student listens to row-by-row table; can replay row.
- **BT-129** Coordinator uploads physics practice with truth tables; template handles.
- **BT-130** Dev refines phrasing per HUJI feedback; bench validates.

## Edge / Misuse / Recovery
- Edge: table without headers; default phrasing.
- Misuse: dev simplifies template; QA catches.
- Recovery: rollback PR.

## Open Questions
- Domain-specific phrasing.

