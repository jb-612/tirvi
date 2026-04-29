<!-- DERIVED FROM docs/business-design/epics/E09-player-ui/stories/E09-F03-word-sync-highlight.stories.md @ sha:2af7279d515d1177f3f9774c0aeae63996e2b2e7 at 2026-04-29T21:09:31Z -->
<!-- Edit upstream and re-import; direct edits will trigger drift detection. -->

# E09-F03 — Word-Sync Highlight (Web Audio API + Timing)

## Source Basis
- PRD: §6.6 (word-level highlight)
- HLD: §3.1 frontend sync model
- Research: src-003 §8.2 (alignment ≤ 80 ms)
- Assumptions: ASM10

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | follows word with audio | focus aid | precise highlight |
| P09 Frontend Dev | implements sync | timing drift | budget |
| P02 Coordinator | demos to peers | reliable demo | smooth highlight |

## Collaboration Model
1. Primary: frontend dev.
2. Supporting: a11y consultant.
3. System actors: HTML `<audio>` + Web Audio API, timings.json.
4. Approvals: a11y review.
5. Handoff: timing → DOM highlight.
6. Failure recovery: timing missing → block-level highlight only.

## Behavioural Model
- Hesitation: dyslexic students have varying preferences for highlight intensity.
- Rework: high-contrast mode adjusts.
- Partial info: timing partial → stop highlighting at last known word.
- Retry: re-fetch on cache invalidation.

---

## User Stories

### Story 1: Word highlights in time with audio

**As a** student
**I want** the current word to be visually highlighted as it is spoken
**So that** I can follow precisely.

#### Main Flow
1. Player loads timings.json.
2. As audio plays, `currentTime` is consulted; matching word receives highlight class.
3. CSS animation respects `prefers-reduced-motion`.

#### Edge Cases
- Audio rate ≠ 1×; timings rescaled.
- Replay sentence; highlight resets cleanly.

#### Acceptance Criteria
```gherkin
Given timings.json + audio for a block
When playback runs at 1× speed
Then the highlighted word matches the spoken word within ±80 ms
```

#### Dependencies
- DEP-INT to E08-F01 (timing).

#### Non-Functional Considerations
- Accessibility: WCAG 2.2 AA contrast on highlight.
- Performance: animation frame budget.

#### Open Questions
- Highlight style customization (color/underline).

---

### Story 2: Speed adjusts highlight without drift

**As a** student
**I want** to slow audio to 0.6× and still see correct highlights
**So that** I can study at my pace.

#### Main Flow
1. User adjusts speed.
2. Player rescales timings (linear).
3. Highlight stays within budget at all rates.

#### Edge Cases
- Very slow speed (0.5×); pitch handling.

#### Acceptance Criteria
```gherkin
Given playback at 0.6× speed
When the audio plays
Then highlight error remains ≤ 80 ms
```

#### Dependencies
- DEP-INT to E09-F04 (speed control).

#### Non-Functional Considerations
- Performance: smooth on mid-range laptop.

#### Open Questions
- Pitch correction at slow speeds.
