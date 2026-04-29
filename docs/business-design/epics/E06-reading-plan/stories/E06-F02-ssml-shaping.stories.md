# E06-F02 — SSML Shaping Per Block Type

## Source Basis
- HLD: §5.2 SSML shaping (slow/emphasized question stems; `<break>` between answers)
- Research: src-003 §2.3 (SSML support varies; Chirp 3 HD does NOT support SSML; Wavenet does)
- Assumptions: ASM03

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | hears clear pacing | breathless rendition | emphasis + pause |
| P08 Backend Dev | encodes SSML | provider variance | per-voice SSML profile |
| P02 Coordinator | reads questions for class | pacing matters | block-type-aware |

## Collaboration Model
1. Primary: backend dev.
2. Supporting: TTS adapter dev (E07).
3. System actors: voice routing (E07-F04), block taxonomy.
4. Approvals: SSML profile changes via review.
5. Handoff: SSML embedded in `plan.json`.
6. Failure recovery: SSML stripped to plain text if voice rejects.

## Behavioural Model
- Hesitation: dev unsure between `<break time="500ms"/>` and `<break strength="medium"/>`.
- Rework: voice ignores `<emphasis>`; switch profile.
- Partial info: provider deprecates an attribute; profile updated.
- Retry: SSML smoke test on every adapter change.

---

## User Stories

### Story 1: Question stems read slower and emphasized

**As a** student
**I want** question stems read slowly with light emphasis
**So that** I can absorb the question before the answers.

#### Main Flow
1. SSML profile maps `block_type=question_stem` to slow + emphasis.
2. `<prosody rate="0.95">` + `<emphasis level="moderate">` wrap the block content.

#### Edge Cases
- Voice ignores `<emphasis>`; alternative `<prosody pitch="+5%">` used.
- Long question (>30 words): auto-split with mid-block break.

#### Acceptance Criteria
```gherkin
Given a question_stem block
When SSML is generated
Then it includes `<prosody rate="0.95">` and an emphasis hint
```

#### Dependencies
- DEP-INT to E07-F01..F03 voice adapters.

#### Non-Functional Considerations
- Quality: pacing perceived by MOS panel as "natural for exam".

#### Open Questions
- Is rate variation evidence-backed for dyslexic listeners?

---

### Story 2: Answer options separated by pause

**As a** student
**I want** clear pauses between answer options
**So that** I can think between options.

#### Main Flow
1. Profile inserts `<break time="700ms"/>` between consecutive answer_option blocks of the same parent question.

#### Edge Cases
- Single-option question (rare): no extra break.

#### Acceptance Criteria
```gherkin
Given 4 answer options for question 4
When SSML is generated
Then 3 pause breaks are present between options
```

#### Dependencies
- DEP-INT to E02-F05 (parent_question_no).

#### Non-Functional Considerations
- Accessibility: pacing accommodates accommodation needs.

#### Open Questions
- Per-student pause customization (post-MVP)?
