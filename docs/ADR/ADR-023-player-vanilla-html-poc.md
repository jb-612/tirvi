# ADR-023: POC player ships as vanilla HTML; Next.js deferred to MVP

**Status:** Proposed

## Context

HLD §3.1 specifies Next.js / React + Tailwind for the player. POC is
a single-PDF, single-page synchronous demo (PLAN-POC.md). Setting up
a Next.js project, build chain, and deployment for one HTML page that
plays a pre-baked audio file is overhead the demo does not earn back.
F36 also ships only four buttons; React's value compounds with form
state and routing that the POC does not have.

## Decision

POC ships a **vanilla** static HTML page (`tirvi/player/index.html`)
with three small `.js` files (`player.js`, `timing.js`,
`highlight.js`). Served by `python -m http.server` from the project
root; the audio + timings come from `drafts/<sha>/`. No build step,
no bundler, no node_modules.

When MVP picks up upload UI, multi-page navigation, and an
authenticated session, the POC HTML is replaced wholesale by a
Next.js port; the data contract (`audio.json`, `page.json`) is the
stable surface that survives.

## Consequences

Positive:
- Zero scaffolding cost; the demo page is a 30-line HTML file.
- Easy to inspect in DevTools without a sourcemap chain.
- The data contracts (`audio.json` + `page.json`) are the only thing
  MVP must keep stable when migrating to Next.js.

Negative:
- No accessibility primitives from a UI framework (manual ARIA + WCAG
  pass for POC; formal audit deferred).
- Repeated reload during iteration (no HMR).
- POC code is throwaway by design — MVP rewrites the player from
  scratch behind the same data contract.

## Alternatives

- **Next.js / React from day one (HLD §3.1).** Rejected for POC: setup
  cost vs single-PDF demo value; iteration speed loss outweighs the
  framework benefit on one HTML page.
- **Streamlit / Gradio.** Rejected: not aligned with HLD's eventual
  Next.js direction; ports of demo state to MVP would be awkward.

## References

- HLD §3.1 — Frontend (Next.js / React + Tailwind)
- PLAN-POC.md — F35 scope: "Vanilla HTML + Web Audio API; no framework"
- Biz corpus E09-F03
- Stable surface schemas (post-review C7): `docs/schemas/audio.schema.json`,
  `docs/schemas/page.schema.json` — pinned wire formats for MVP migration
- Related: N04/F35 design.md DE-01; N04/F36 (4-control player); F22 DE-07
  produces `page.json`; F30 produces `audio.json`
