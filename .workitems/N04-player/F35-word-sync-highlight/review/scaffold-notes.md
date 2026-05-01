# F35 — Scaffold + TDD Notes (wave2-scaffold)

Date: 2026-05-01
Owner: wave2-scaffold (autonomous)

## What was scaffolded / TDD'd

Tasks T-04, T-05, T-06 — all green via Vitest.

| Task | Symbol | File | Tests |
|------|--------|------|-------|
| T-04 | `lookupWord(timings, tSeconds)` | `player/js/highlight.js` | 7 — boundaries, half-open intervals, null tail, 1000-mark binary-search smoke |
| T-05 | `positionMarker(bbox, naturalDims, renderedDims)` | `player/js/highlight.js` | 6 — 1:1, downscale, retina-style upscale, anisotropic, defensive zero, integer rounding |
| T-06 | `--highlight-bg/--highlight-fg` tokens, `prefers-reduced-motion` media + `.no-animation` class | `player/player.css` | 3 — WCAG contrast helper (≥ 4.5:1), prefers-reduced-motion CSS rule, `:focus-visible` rule |

## Test runner reality

`tasks.md` lists `test_file: tests/unit/test_*.py` for every task. Reality:
`player/` is a Vitest + jsdom sub-project with `player/test/*.spec.js` already
hosting T-01..T-03. New T-04..T-06 tests landed in
`player/test/highlight.spec.js`. Logged in `dispute-item.md` (D1) for
follow-up doc reconciliation.

## Layer coverage

- **L1 (structure)**: existing — `player/js/`, `player/test/` dirs intact.
- **L2 (contracts)**: JSDoc typedefs added for `Timing`, `lookupWord` half-open
  semantics, `positionMarker` return shape `{top, left, width, height}`.
- **L3/L4 (domain + behaviour)**: `lookupWord` is a pure binary search;
  `positionMarker` is a pure scaling function returning a CSS-ready dict.
- **L5 (TDD readiness)**: 16 new specs in `highlight.spec.js`; full vitest
  suite 84/84.
- **L6 (runtime)**: `main.js` already wires `findActiveMark` via
  `startHighlightLoop`. `lookupWord` exported alongside for future loop
  swap (out of scope for T-04..T-06 — would need a perf gate first).
- **L7 (traceability)**: feature `traceability.yaml` not edited; tests
  reference AC IDs in describe/it blocks per project convention.

## Test delta

`npm test` in `player/`: 42 → 84 (added 42).

## Disputes flagged

See repo-root `dispute-item.md`:
- D1 — tasks.md `test_file:` paths point to Python; reality is Vitest/JS.
- D3 — aria-keyshortcuts choice for Continue/Pause both = "Space".
