# F36 — Scaffold + TDD Notes (wave2-scaffold)

Date: 2026-05-01
Owner: wave2-scaffold (autonomous)

## What was scaffolded / TDD'd

Tasks T-02 through T-06 — all green via Vitest.

| Task | Symbol | File | Tests |
|------|--------|------|-------|
| T-02 | `nextState(state, event)` pure function | `player/js/controls.js` | 7 — every legal transition + invalid no-ops |
| T-03 | `mountControls({audio, toolbar})` | `player/js/controls.js` | 7 — 4-button DOM, click → dispatch → audio side effects, audio.ended → ended state, .play() rejection no-throw |
| T-04 | `disabledFor(state)` + DOM render | `player/js/controls.js` | 4 (table) + 3 (DOM) — idle/playing/paused/ended button matrix |
| T-05 | `bindKeyboard(controls, root)` | `player/js/controls.js` | 6 — Space (idle/playing/paused/ended toggle), R lower/upper case, preventDefault |
| T-06 | aria-label he+en, aria-keyshortcuts, focus contract | `player/js/controls.js` + `player/player.css` | 3 — bilingual aria-label per button, Space/R keyshortcut attrs, focus delegation |

## Scope expansion vs POC-CRITICAL-PATH.md

Prior `controls.js` mounted ONE play button (T-01 only) and a comment cited
`POC-CRITICAL-PATH.md` as deferring T-02..T-06 to v0.1. The team-lead brief
explicitly assigned T-02..T-06 in this run, so I expanded
`mountControls` to mount the full 4-button toolbar with the state machine
wired to audio side effects. `mountPlayButton` is preserved as a
back-compat alias so `main.js`'s existing import path still works (returns
the Play button from the new toolbar). Logged in `dispute-item.md` (D2)
for human reconciliation.

## Layer coverage

- **L1 (structure)**: `player/js/controls.js` existed; same file expanded.
- **L2 (contracts)**: JSDoc typedefs `PlayerState`, `PlayerEvent`. Public
  API: `nextState`, `disabledFor`, `mountControls`, `bindKeyboard`,
  `mountPlayButton` (back-compat).
- **L3 (domain)**: `nextState` is the sole source of state truth — total
  function over `PlayerState × PlayerEvent`, invalid transitions return
  current state unchanged (matches design.md L48–L50).
- **L4 (behaviour)**: button click + audio.ended event are the only
  inputs; `applyAudio` and `applyDisabled` are the only side effects.
- **L5 (TDD readiness)**: 27 new specs in `controls.spec.js`; full vitest
  suite 84/84.
- **L6 (runtime)**: `main.js` still imports `mountPlayButton` →
  back-compat preserved.
- **L7 (traceability)**: tests reference AC IDs (`us_01_ac_01`,
  `us_02_ac_01`, `us_03_ac_01`) in test names per project convention.

## Test delta

`npm test` in `player/`: 42 → 84 (added 42 across F35 + F36 in this run).

## Disputes flagged

See repo-root `dispute-item.md`:
- D1 — tasks.md `test_file:` paths point to Python; reality is Vitest/JS.
- D2 — POC-CRITICAL-PATH.md deferral vs team-lead brief.
- D3 — aria-keyshortcuts choice (`Space` for Play/Pause/Continue, `R` for Reset).
