---
title: Stub run badge [s] in version history panel
created: 2026-05-01
status: raw
next: design
---

## Idea

When `run_demo.py --stubs` produces a draft, write a `meta.json` file
into `drafts/<sha>/` containing `{"stub": true}`. `build_versions_list()`
reads this and appends ` [s]` to the label so stub runs are visually
distinct from real pipeline runs in the player's version history panel.

## Why now

UAT revealed that the history panel shows stub runs alongside real runs
with no visual distinction. During development, both types of runs
accumulate and it is unclear which entries are meaningful.

## Open questions

- Badge format: ` [s]` suffix, or a separate icon/color class in the UI?
- Should `meta.json` carry other flags in future (e.g., `{"model": "stub",
  "pages": 1}`)?
- Does the badge need to appear in the `<title>` / page heading too?

## Suggested next step

Small enough for `@hotfix` — 3 files: `scripts/run_demo.py` (write
meta.json + filter it from version list), `player/js/version-nav.js`
(render label with badge).
