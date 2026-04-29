# E09-F04 — Controls (Play/Pause, Speed, Repeat, Next/Prev, Font Size, Contrast)

## Source Basis
- PRD: §6.6 controls; §7.1 Accessibility
- HLD: §3.1 controls
- Research: src-003 §7 principle 7
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | full control | fumbling | discoverable controls |
| P09 Frontend Dev | implements controls | many surfaces | shared component lib |
| P02 Coordinator | demos controls | clarity | tooltips |

## Collaboration Model
1. Primary: frontend dev.
2. Supporting: a11y consultant.
3. System actors: control surfaces, audio engine, theme system.
4. Approvals: a11y review.
5. Handoff: control change → audio engine.
6. Failure recovery: bad input → revert to last good.

## Behavioural Model
- Hesitation: student new to controls.
- Rework: speed range needs adjusting.
- Partial info: keyboard shortcuts unknown; help dialog.
- Retry: tap to skip during playback.

---

## User Stories

### Story 1: Speed slider 0.5×–1.5×

**As a** student
**I want** smooth speed control between 0.5× and 1.5×
**So that** I can study at my pace.

#### Main Flow
1. Slider with 0.05× steps.
2. Audio playbackRate updates instantly.
3. Highlight rescales (E09-F03 Story 2).

#### Edge Cases
- Bound at 0.5 and 1.5 by design.

#### Acceptance Criteria
```gherkin
Given the slider at 0.6×
When audio plays
Then audio rate matches and highlight stays in budget
```

#### Dependencies
- DEP-INT to E09-F03.

#### Non-Functional Considerations
- Accessibility: keyboard arrow steps.

---

### Story 2: Repeat sentence

**As a** student
**I want** a one-tap "repeat sentence" button
**So that** I can re-listen without scrubbing.

#### Main Flow
1. Player tracks current sentence boundaries (from plan.json).
2. Tap → seek to start; replay.

#### Edge Cases
- At sentence boundary; choose previous sentence (configurable).

#### Acceptance Criteria
```gherkin
Given audio is playing inside a sentence
When repeat-sentence is pressed
Then audio seeks to that sentence start and re-plays
```

#### Dependencies
- DEP-INT to E08-F04 sentence boundaries.

#### Non-Functional Considerations
- Accessibility: keyboard `R`.

---

### Story 3: Font size + high contrast modes

**As a** student
**I want** larger text and high-contrast theme
**So that** I can read clearly.

#### Main Flow
1. Toggle controls in toolbar.
2. CSS vars for size and theme.

#### Edge Cases
- Very large size on small viewport; horizontal scroll.

#### Acceptance Criteria
```gherkin
Given high-contrast toggle is on
When the player renders
Then text and controls meet ≥ 7:1 contrast
```

#### Non-Functional Considerations
- Accessibility: WCAG AAA contrast for high-contrast mode.

#### Open Questions
- Persist preferences in `localStorage`?
