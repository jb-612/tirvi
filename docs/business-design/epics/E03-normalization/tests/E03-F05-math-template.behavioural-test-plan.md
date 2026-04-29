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
