# E02-F04 — Block-Level Structural Detection

## Source Basis
- PRD: §6.2 (block types: heading, instruction, question stem, answer option, paragraph, table, figure caption)
- HLD: §5.1 input (block-segmented Hebrew text)
- Research: src-003 §3 (architecture change #4 keeps bboxes for downstream); §8.2 quality gates (block recall)
- Assumptions: ASM01 (practice-mode framing — block fidelity is product moat)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears "question 4" only | reading whole page | per-block playback |
| P08 Backend Dev | builds detector | mixed RTL/LTR layout | rules + heuristics |
| P02 Coordinator | needs answer-only mode | answer choices read together | "answers" affordance |

## Collaboration Model
1. Primary: backend dev defining block taxonomy.
2. Supporting: lexicon maintainer (acronym list shapes detection).
3. System actors: Tesseract output, layout post-processor.
4. Approvals: block taxonomy change → docs + tests.
5. Handoff: tagged blocks → E02-F05 question/answer numbering → E03 normalization.
6. Failure recovery: low-confidence block tag goes to `paragraph` default.

## Behavioural Model
- Hesitation: detector unsure between `instruction` and `question_stem`.
- Rework: false-positive table; collapse to paragraph.
- Partial info: figure caption with no figure; tag as `figure_caption` orphan.
- Retry: block detection re-run after layout fixup.

---

## User Stories

### Story 1: Pages segmented into typed blocks

**As a** student
**I want** the page text grouped by block type
**So that** I can ask the player to read just the question or just the answers.

#### Preconditions
- `OCRResult` with bboxes + lang hints.

#### Main Flow
1. Block detector consumes OCR output; uses heuristics (font size, indentation, numbering, regex).
2. Tags each region as one of: `heading`, `instruction`, `question_stem`, `answer_option`, `paragraph`, `table`, `figure_caption`, `math_region`.
3. Emits `pages[].blocks[]` with `block_id`, `block_type`, `bbox`, child word refs.

#### Edge Cases
- Multi-question page; questions enumerated.
- Table with merged cells: detector returns table region with row hints (E02-F05).
- Figure with no caption text: `figure_caption=null`; figure region tagged `figure`.

#### Acceptance Criteria
```gherkin
Given a 2-question page with a 4-option answer set per question
When block segmentation runs
Then 2 question_stem blocks and 8 answer_option blocks are emitted
And each block has a unique block_id and bbox
```

#### Data and Business Objects
- `Block` (block_id, type, bbox, language_hint, child_word_refs).

#### Dependencies
- DEP-INT to E02-F03 (OCRResult), E02-F05 (numbering), E03 (normalization).

#### Non-Functional Considerations
- Quality gate: block-segmentation recall ≥ 95% questions / ≥ 90% answers (src-003 §8.2).
- Reliability: low-confidence default keeps pipeline alive.

#### Open Questions
- Should we use a learned model post-MVP rather than heuristics?

---

### Story 2: Math regions routed via dedicated template

**As a** student studying math Bagrut
**I want** equations to be read with a math template, not flat
**So that** "x squared" beats "x two".

#### Preconditions
- Math detector heuristics in place.

#### Main Flow
1. Detector flags `math_region` blocks via symbol density / LaTeX-like notation.
2. E03 normalization routes math region through math template (E03-F05).
3. SSML emits Hebrew math reading ("x בריבוע" for x²).

#### Edge Cases
- Inline math in a Hebrew paragraph: detector flags inline span.
- Misclassified math (chemistry): user feedback corrects.

#### Acceptance Criteria
```gherkin
Given a page with an equation "x² + y² = z²"
When detection runs
Then a `math_region` block is emitted with the equation text
```

#### Dependencies
- DEP-INT to E03-F05 (math template).

#### Non-Functional Considerations
- Quality: math-detection precision ≥ 90% on tirvi-bench math pages.

#### Open Questions
- Bring SRE / MathSpeak Hebrew localization in MVP or v1.1?
