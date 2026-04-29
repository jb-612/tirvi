# E09-F06 — WCAG 2.2 AA Conformance

## Source Basis
- PRD: §7.1 Accessibility
- HLD: §3.1 frontend a11y
- Research: src-003 §7 principle 7
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student with LD | usable UI | tooling barriers | WCAG AA |
| P09 Frontend Dev | enforces a11y | manual fixes | a11y CI checks |
| P02 Coordinator | confidence in product | invisible barriers | external audit |

## Collaboration Model
1. Primary: frontend dev + a11y consultant.
2. Supporting: tester with assistive tech.
3. System actors: keyboard nav, screen reader, contrast tools.
4. Approvals: a11y manual audit.
5. Handoff: a11y report → product release gate.
6. Failure recovery: violations block release.

## Behavioural Model
- Hesitation: student with screen reader unsure if app supports it.
- Rework: contrast violation found late; fix early via CI.
- Partial info: ARIA gaps; manual audit catches.
- Retry: keyboard rerouting.

---

## User Stories

### Story 1: Keyboard-first navigation

**As a** student
**I want** to navigate every action by keyboard
**So that** I do not need a mouse.

#### Main Flow
1. Tab order well-defined.
2. Focus ring always visible (≥ 3:1 contrast).
3. Shortcut help available via `?`.

#### Acceptance Criteria
```gherkin
Given the player is loaded
When the user presses Tab
Then focus follows a logical sequence
And every interactive element is reachable
```

#### Dependencies
- DEP-INT to E09-F02..F05.

#### Non-Functional Considerations
- Accessibility: WCAG 2.2 SC 2.1.1.

---

### Story 2: Screen-reader friendly

**As a** student using VoiceOver / NVDA
**I want** announcements that match the visual UI
**So that** I can use the app without sighted help.

#### Main Flow
1. ARIA roles applied to player surfaces.
2. Live regions announce state changes (preparing, playing, paused).

#### Acceptance Criteria
```gherkin
Given a student presses play
When the screen reader is on
Then "playing question 5" is announced
```

#### Non-Functional Considerations
- Accessibility: SC 4.1.2.

---

### Story 3: Contrast and reduced motion

**As a** sensitive student
**I want** `prefers-reduced-motion` honored and ≥ 4.5:1 contrast everywhere
**So that** I am not overwhelmed.

#### Main Flow
1. `@media (prefers-reduced-motion: reduce)` disables non-essential animations.
2. Contrast checks in CI.

#### Acceptance Criteria
```gherkin
Given the OS prefers reduced motion
When the player renders
Then no autoplay animations run beyond essential feedback
```

#### Non-Functional Considerations
- Accessibility: SC 2.3.3 / 1.4.3.

#### Open Questions
- WCAG 2.2 AAA targets for high-contrast mode.
