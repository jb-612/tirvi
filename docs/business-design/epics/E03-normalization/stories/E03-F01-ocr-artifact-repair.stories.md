# E03-F01 — OCR Artifact Repair

## Source Basis
- PRD: §6.3 Hebrew normalization
- HLD: §3.3 normalize stage; §5.1 cleaned input
- Research: src-003 §10 Phase 2 F3.1
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | reads cleaned text | broken lines / stray punctuation | repaired text |
| P08 Backend Dev | implements repair | RTL/LTR direction errors | rules library |
| P02 Coordinator | uploads scans | scanner artifacts | mostly invisible repair |

## Collaboration Model
1. Primary: backend dev maintaining repair rules.
2. Supporting: lexicon maintainer (publisher-specific patterns).
3. System actors: Block detector (E02-F04), reading-plan generator (E06).
4. Approvals: rule additions via review checklist.
5. Handoff: repaired text into NLP (E04).
6. Failure recovery: low-confidence repair → flagged for SRE attention.

## Behavioural Model
- Hesitation: dev unsure if repair is too aggressive (might erase intent).
- Rework: rule over-fits one publisher; bench page added.
- Partial info: directionality ambiguous in mixed paragraph; default to context.
- Abandoned flow: repaired text rejected by NLP (Hebrew morph fails); rolled back per page.

---

## User Stories

### Story 1: Broken-line OCR is rejoined into sentences

**As a** student
**I want** broken sentence fragments rejoined
**So that** the audio reads complete thoughts.

#### Main Flow
1. Normalizer scans `OCRResult.pages[].words` for line breaks within a sentence.
2. Heuristics: hyphenation, mid-word break across two `word` items, sentence-final punctuation absent.
3. Repaired text emitted as `pages[].normalized_text` with stable bbox→text spans.

#### Edge Cases
- Word genuinely split across page (bbox proves it); rejoin only intra-page.
- Hyphen within compound word (`לוֹחַ-זמנים`); preserved.

#### Acceptance Criteria
```gherkin
Given a column where line break splits a Hebrew word
When normalization runs
Then the repaired output joins the word
And the bbox→text mapping preserves both source bboxes
```

#### Data and Business Objects
- `NormalizedText` (text, span_index → bbox refs).

#### Dependencies
- DEP-INT to E02-F03 (OCRResult), E04 (NLP consumes repaired text).

#### Non-Functional Considerations
- Reliability: deterministic per input.
- Auditability: per-rule application logged for debugging.

#### Open Questions
- Should we expose a repair-diff to SRE/QA?

---

### Story 2: Stray punctuation cleaned without erasing meaningful glyphs

**As a** dev
**I want** stray punctuation (artifacts of OCR) stripped without removing real punctuation
**So that** the NLP layer receives clean input.

#### Main Flow
1. Per-page rules drop low-confidence bbox tokens that match a known artifact pattern.
2. Real punctuation preserved (`.`, `,`, `;`, `?`, `:`, Hebrew quotes).

#### Edge Cases
- Hebrew geresh (`׳`) inside acronym (e.g., `מס׳`): preserved (E03-F03).
- Mid-line quotation marks: preserved.

#### Acceptance Criteria
```gherkin
Given OCR introduced 5 stray comma artifacts on a page
When normalization runs
Then the artifacts are removed
And all sentence-final punctuation is preserved
```

#### Dependencies
- DEP-INT to E03-F03 (acronym lexicon).

#### Non-Functional Considerations
- Quality: false-positive removal ≤ 1% per bench.
- Reliability: rule changes hit bench before merge.

#### Open Questions
- Are we OK with deterministic but imperfect repair, or aim for ML-based?
