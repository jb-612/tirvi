---
feature_id: N04/F36
feature_type: ui
status: drafting
hld_refs:
  - HLD-§3.1/Frontend
prd_refs:
  - "PRD §6.6 — Player controls"
  - "PRD §7.1 — Accessibility"
adr_refs: [ADR-023]
biz_corpus: true
biz_corpus_e_id: E09-F04
---

# Feature: Accessibility Controls (4-button POC)

## Overview

Minimum POC control surface bound to the same vanilla HTML page F35
ships. POC scope is exactly four controls — Play, Pause, Continue,
Reset — driving a tiny state machine over the `<audio>` element.
Speed slider, repeat-sentence, font size, and high-contrast toggle
(biz US-01..US-03) lift to MVP. Keyboard shortcuts stay minimum
(`Space` for play/pause-toggle, `R` for reset). ARIA labels +
WCAG-compliant focus rings give POC a basic accessibility floor; full
WCAG AA audit pipeline is deferred per HLD §11.

## Dependencies

- Upstream: N04/F35 (vanilla HTML page hosts the buttons).
- Adapter ports consumed: none.
- External services: none.
- Downstream: none — F36 is the leaf player surface for POC.

## Interfaces

| Module | Symbol | Kind | Notes |
|--------|--------|------|-------|
| `tirvi/player/index.html` | `<button>` × 4 | DOM | Play / Pause / Continue / Reset; bound to F35's `<audio id="audio">` |
| `tirvi/player/controls.js` | `Controls` class | module | binds DOM, owns state machine |
| `tirvi/player/controls.js` | `PlayerState = "idle" \| "playing" \| "paused" \| "ended"` | type | exhaustive POC states |
| `tirvi/player/keymap.js` | `bindKeyboard(controls)` | function | Space toggles play/pause, R resets |

State transitions:
- `idle` → Play → `playing`
- `playing` → Pause → `paused`
- `paused` → Continue → `playing`
- any → Reset → `idle`
- `<audio>` `ended` event → `ended`
- `ended` → Play → `playing` (from start) — same as idle

## Approach

1. **DE-01**: Button DOM scaffold — 4 `<button>` elements with
   `id="btn-play|pause|continue|reset"` and ARIA labels in Hebrew +
   English (`aria-label="Play / נגן"` style); `<kbd>` text under each
   names the shortcut.
2. **DE-02**: Player state machine — pure function
   `next_state(current, event) -> PlayerState`; events =
   `{play, pause, continue, reset, audio_ended}`; rejects invalid
   transitions silently (no exceptions in UI).
3. **DE-03**: Event handlers — each button click dispatches the
   matching event; the state-machine output drives `audio.play()`,
   `audio.pause()`, or `audio.currentTime = 0; audio.pause()`.
4. **DE-04**: Button enable/disable — render function flips
   `button.disabled` per state (e.g., Continue is disabled in `idle`
   and `playing`, enabled only in `paused`).
5. **DE-05**: Keyboard shortcuts — `Space` dispatches
   play/pause-toggle (mapped to current state); `R` always dispatches
   reset; both `event.preventDefault()` to avoid page scroll.
6. **DE-06**: ARIA + focus + WCAG — focus ring always visible (CSS
   `:focus-visible`); button color tokens reuse F35's
   `--highlight-bg/fg` palette so contrast ≥ 4.5:1 (AA);
   `aria-keyshortcuts` advertises the keymap.

## Design Elements

- DE-01: buttonScaffold (ref: HLD-§3.1/Frontend)
- DE-02: playerStateMachine (ref: HLD-§3.1/Frontend)
- DE-03: buttonEventHandlers (ref: HLD-§3.1/Frontend)
- DE-04: enableDisablePerState (ref: HLD-§3.1/Frontend)
- DE-05: keyboardShortcuts (ref: HLD-§3.1/Frontend)
- DE-06: ariaFocusContrast (ref: HLD-§3.1/Frontend)

## Decisions

- D-01: Vanilla HTML stack → **ADR-023** (existing; F35 / F36 share).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Speed slider 0.5–1.5× | Out of scope | PLAN-POC.md F36: 4 controls only |
| Repeat-sentence | Out of scope | POC ships `Reset` only (full restart) |
| Font size + contrast toggles | Out of scope | Demo image is fixed page; size/contrast deferred MVP |
| WCAG AAA contrast for high-contrast mode | POC ships AA on default theme only | Full WCAG audit pipeline deferred per HLD §11 |
| `localStorage` preference persistence | Out of scope | POC has no preferences to persist |

## HLD Open Questions

- localStorage persistence → deferred MVP (no prefs to persist in POC).
- Pitch correction at slow speeds → deferred (no slow-speed in POC).
- Soft / bold highlight toggle → tracked in F35 deviations; deferred MVP.

## Risks

| Risk | Mitigation |
|------|-----------|
| Space key triggers page scroll on long pages | DE-05 calls `preventDefault` when focus is in player root |
| Continue button confuses users (vs Play) | DE-04 hides Continue in `idle` / `ended` (only Play is shown); DE-06 tooltip clarifies |
| Reset mid-playback can race with rAF loop | DE-03 dispatches reset which sets `currentTime=0` then `pause()`; F35 rAF loop reads `currentTime` and renders frame from start |

## Diagrams

- `docs/diagrams/N04/F36/state-machine.mmd` — idle / playing / paused / ended state graph

## Out of Scope

- Speed slider; repeat-sentence; font-size + contrast toggles;
  localStorage persistence; pitch correction — all deferred MVP.
