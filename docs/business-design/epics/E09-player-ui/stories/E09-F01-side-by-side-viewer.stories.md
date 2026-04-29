# E09-F01 — Side-by-Side Viewer (PDF Image + Cleaned Text)

## Source Basis
- PRD: §6.6 Player UI ("side-by-side")
- HLD: §3.1 frontend split view
- Research: src-003 §3 (player can mock TTS+timing in week 9)
- Assumptions: ASM01

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P01 Student | sees text + image | scrolling between layouts | side-by-side layout |
| P02 Coordinator | reviews fidelity | text drift from image | aligned scroll |
| P09 Frontend Dev | builds layout | RTL CSS challenges | reliable layout |

## Collaboration Model
1. Primary: frontend dev.
2. Supporting: accessibility consultant.
3. System actors: page image source, cleaned text, layout engine.
4. Approvals: a11y review.
5. Handoff: layout consumes plan + page image.
6. Failure recovery: missing image → text-only fallback.

## Behavioural Model
- Hesitation: student unsure where to focus.
- Rework: mobile narrow screen; layout adapts to stacked.
- Partial info: image not yet loaded; placeholder.
- Retry: image fails to load; fallback to OCR-derived rendering.

---

## User Stories

### Story 1: Page image left, cleaned text right (RTL)

**As a** student
**I want** the page image and cleaned text shown side by side
**So that** I can verify what is being read.

#### Main Flow
1. Layout: `<main>` with two columns; right column displays text in RTL.
2. Smooth scroll synchronization (image scroll → text scroll proportional).
3. WCAG focus / contrast respected.

#### Edge Cases
- Mobile narrow: stacked; toggle which is on top.
- Very long page: virtualized scroll.

#### Acceptance Criteria
```gherkin
Given a 5-page document with images
When the player loads
Then page 1 image and text are visible side by side
And the layout adapts to mobile viewport
```

#### Data and Business Objects
- `PageImage`, `RenderedText` (sourced from `pages/{doc}/{page}.norm.json`).

#### Dependencies
- DEP-INT to E01-F03 (status), E06 (plan), E11-F01 (image TTL).

#### Non-Functional Considerations
- Accessibility: WCAG 2.2 AA.
- Performance: TTI < 2 s on mid laptop.
- Privacy: image fetched via signed URL; no third-party CDN.

#### Open Questions
- Toggle to text-only mode for low-bandwidth.

---

### Story 2: Sync scroll between panels

**As a** student
**I want** scrolling the image to scroll the text proportionally
**So that** I stay oriented.

#### Main Flow
1. Scroll listener tracks image position.
2. Text panel scrolls to matching block via bbox→block map.

#### Edge Cases
- User scrolls text directly; image follows.
- Out-of-sync after window resize; resync on scroll-stop.

#### Acceptance Criteria
```gherkin
Given a doc with 3 blocks per page
When student scrolls image
Then text scrolls proportionally and the active block highlights
```

#### Dependencies
- DEP-INT to E02-F03 (bbox refs).

#### Non-Functional Considerations
- Accessibility: `prefers-reduced-motion` honored.

#### Open Questions
- Snap-to-block on scroll-stop?
