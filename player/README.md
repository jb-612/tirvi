# tirvi POC player (F35 + F36)

Vanilla HTML + Web Audio API; no framework. Per ADR-023, this is the POC
shape; MVP migration to Next.js is deferred.

## Layout

```
player/
  index.html           — F35 page shell
  player.css           — F35 styles
  js/
    player.js          — F35 state init + audio.json/page.json loader
    timing.js          — F35 audio.json parser
    highlight.js       — F35 rAF highlight loop + bbox positioning
    controls.js        — F36 4-button controls + state machine + keyboard
  test/                — JS unit tests (Jest/Vitest — toolchain TBD)
```

## Wire contracts (read-only)

- `audio.json` — `docs/schemas/audio.schema.json` (produced by F30)
- `page.json`  — `docs/schemas/page.schema.json` (produced by F22 DE-07)
- `audio.mp3` — produced by F26

## Test toolchain (deferred)

L4 testing for F35/F36 cannot be Python pytest. The scaffold ships only
JSDoc + module exports. Before `/tdd` on these features, set up
`package.json` + Jest (or Vitest) with jsdom. Targeted tests:

- `player.js`: stub `audio.json` + `page.json`, assert state initialization
- `timing.js`: schema validation, sort stability, edge cases (empty list)
- `highlight.js`: rAF tick → marker position, retina scaling
- `controls.js`: state transitions (`nextState` pure function), keyboard handlers

## Static serve (POC demo)

```
python3 -m http.server --directory player/ 8000
```

Open <http://localhost:8000>; expects `audio.json`, `page.json`, `page-1.png`,
`audio.mp3` colocated in the served directory (or under `drafts/<sha>/`).
