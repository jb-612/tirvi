# E09-F02 — Per-Block Play Affordances ("read question only" / "read answers only")

## Source Basis
- PRD: §6.6 (distinct affordances)
- HLD: §3.1 frontend
- Research: src-003 §1 (block-aware playback is the moat)
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | precise navigation | rewinding inside block | per-block buttons |
| P02 Coordinator | demos affordances | discoverability | clear UI |
| P09 Frontend Dev | builds affordances | consistent across block types | block-type-aware |

## Collaboration Model
1. Primary: frontend dev.
2. Supporting: accessibility.
3. System actors: player, plan.json, voice routing.
4. Approvals: a11y review.
5. Handoff: button click → audio request.
6. Failure recovery: audio not yet ready → "preparing" state.

## Behavioural Model
- Hesitation: student new to UI; tooltips help.
- Rework: button placement debated; UX testing iterates.
- Partial info: only some answers ready; UI surfaces.
- Retry: tap-tap rapid; rate-limit prevents abuse.

---

## User Stories

### Story 1: Read question only

**As a** student
**I want** a button on each question stem to play just that stem
**So that** I can focus before answers.

#### Main Flow
1. Block of type `question_stem` renders with a "play" affordance + question_no.
2. Click → play just that block's audio.
3. Highlight word-by-word within block.

#### Edge Cases
- Question stem split across page (rare); play continues across pages.
- Audio not ready; affordance dimmed with "preparing".

#### Acceptance Criteria
```gherkin
Given the player loads page 2 with question 5
When the user clicks "play question 5"
Then only question 5 audio plays
```

#### Dependencies
- DEP-INT to E02-F05 (numbering), E08-F01 (timing).

#### Non-Functional Considerations
- Accessibility: ARIA role + label per block.

#### Open Questions
- Long-press = spell-out per word?

---

### Story 2: Read answers only

**As a** student
**I want** a single "play answers" button per question
**So that** I hear all options as a sequence.

#### Main Flow
1. Affordance grouped under question stem.
2. Click → plays answer_option blocks in order with pauses (E06-F02).

#### Edge Cases
- Single answer option (rare); plays single option.

#### Acceptance Criteria
```gherkin
Given question 5 has 4 answers
When user clicks "play answers"
Then all 4 answers play in order with breaks
```

#### Dependencies
- DEP-INT to E06-F02, E02-F05.

#### Non-Functional Considerations
- Accessibility: keyboard equivalent (Enter / Space).

#### Open Questions
- Per-option highlight style.
