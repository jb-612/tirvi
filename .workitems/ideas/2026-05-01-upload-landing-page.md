---
title: Startup upload landing page — PDF drag-and-drop before player
created: 2026-05-01
status: raw
next: research
---

## Idea

Replace the current CLI-only entry point with a dedicated startup page where
the user drags or selects an exam PDF. The pipeline runs server-side (~30–60s),
progress is surfaced inline, then the page transitions into the player with the
new run already loaded. The player stays a pure reader; ingestion lives on the
landing page.

## Why now

UAT revealed that new runs require a CLI command, which is a dead end for
non-technical users (students, exam coordinators). A landing page is the
natural first touchpoint for a web product serving students with reading
accommodations — it should require zero terminal knowledge.

## Open questions

- Single-page transition (same URL, JS state machine) vs. separate `/upload`
  route vs. server-side redirect to `/<sha>/`?
- How to surface pipeline progress (~30–60s) — polling, SSE, WebSocket?
- RTL upload UI conventions: does the drag-zone label / file name display
  flip, and how do Hebrew screen readers announce upload state?
- Accessibility requirements specific to the accommodations context: what
  WCAG level is expected? Are keyboard-only and screen-reader flows tested?
- File size / page count limits for the MVP upload? Single page only (POC) or
  multi-page?
- Authentication gate before upload (coordinator login) or anonymous?

## Suggested next step

UI/UX research: survey upload-page patterns in accessibility-first products,
Hebrew RTL form conventions, and pipeline-progress feedback patterns. Outputs
feed a concept interview before any HLD.
