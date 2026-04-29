# E02-F05 — Question / Answer Number Tagging

## Source Basis
- PRD: §6.2 (tag question numbers and answer-option letters/numbers)
- HLD: §5.2 SSML shaping (slow/emphasized question numbers; `<break>` between answers)
- Research: src-003 §1 ("question number / answer-option letter tagging" is what generic TTS misses)
- Assumptions: none new

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | "read question 4" | knows which question is which | numbered tagging |
| P08 Backend Dev | implements tagger | varied numbering schemes | regex + heuristics |
| P02 Coordinator | exam navigation | jump to specific answer | `block_id` per option |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: lexicon maintainer (Hebrew ordinals / Latin-letter conventions).
3. System actors: block detector (E02-F04), normalization (E03).
4. Approvals: numbering taxonomy change documented.
5. Handoff: tagged blocks consumed by reading-plan generator (E06) and player (E09).
6. Failure recovery: unknown numbering → default to position-based ID.

## Behavioural Model
- Hesitation: dev unsure whether `א` and `1` map to the same kind of identifier.
- Rework: regex too greedy on dates within answer text; tighter rules.
- Partial info: question 14 has no answer choices visible (next page); detector handles cross-page reference (post-MVP).
- Retry: re-tag on retry if heuristics updated.

---

## User Stories

### Story 1: Question and answer identifiers normalized across schemes

**As a** student
**I want** question 4 to be reachable as "question 4" regardless of whether the original is `4.`, `שאלה 4`, or `סעיף ד`
**So that** I can navigate consistently.

#### Preconditions
- Block detector emits question-stem and answer-option blocks.

#### Main Flow
1. Tagger inspects start of each question_stem block for numbering pattern.
2. Recognizes Arabic numerals, Hebrew ordinals (ראשון, שני…), Hebrew letters (א, ב, ג), Latin (a, b, c, A, B, C).
3. Emits canonical `question_no` (integer) and `display_no` (original).
4. Tagger does same for answer_option (letters / numbers / symbols).

#### Edge Cases
- Sub-questions (4a, 4b): hierarchical numbering; canonical "4.1" for 4a.
- Numbering mid-paragraph (e.g., "see question 4"); tagger ignores in-text references.

#### Acceptance Criteria
```gherkin
Given a page with `שאלה 1`, `שאלה 2`, with answers `א ב ג ד`
When tagging runs
Then `question_no=1, display_no="שאלה 1"` and answers carry `option_no="א"|"ב"|"ג"|"ד"`
```

#### Data and Business Objects
- `Block.question_no`, `Block.option_no`, `Block.display_no`.

#### Dependencies
- DEP-INT to E02-F04, E06, E09.

#### Non-Functional Considerations
- Quality: numbering precision ≥ 95% on tirvi-bench.
- Accessibility: canonical numbering enables consistent ARIA labels.

#### Open Questions
- Hierarchical numbering encoding: dot ("4.1") vs nested ("4a")?

---

### Story 2: Answer-option set anchored to its question

**As a** student
**I want** the answer choices to know they belong to question 4
**So that** "read answers" plays only that question's choices.

#### Preconditions
- Block detector emits answers next to question stems.

#### Main Flow
1. Tagger associates answer-option blocks with the nearest preceding question_stem (within a vertical distance threshold).
2. Emits `parent_question_no` on each answer block.

#### Edge Cases
- Two question stems with answers split across page break: cross-page anchoring (post-MVP).
- Lone answer-option block with no nearby question: emit `parent_question_no=null`; flag for review.

#### Acceptance Criteria
```gherkin
Given question 4 has 4 answer options on the same page
When tagging runs
Then all 4 answer blocks carry `parent_question_no=4`
```

#### Dependencies
- DEP-INT to E09-F02 (player "read answers" affordance).

#### Non-Functional Considerations
- Quality: anchor accuracy ≥ 95%.
- Reliability: orphan answer blocks logged for SRE attention.

#### Open Questions
- Cross-page anchoring scope?
