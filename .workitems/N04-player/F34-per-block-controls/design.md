---
feature_id: N04/F34
feature_type: ui
status: designed
hld_refs:
  - HLD-§3.1/Frontend
prd_refs:
  - "PRD §6.6 — Player controls"
adr_refs: []
biz_corpus_e_id: E09-F02
gate: deferred_mvp   # not scheduled for POC; activate when MVP player begins
---

# Feature: Per-Block Playback Controls

## Overview

Per-block playback controls allow the student to play, pause, and repeat
individual exam blocks (questions, instructions, reading passages) instead
of the entire page. The player surfaces a block-level play button adjacent
to each block boundary, driven by block metadata from N02/F22 (`ReadingPlan`
block partitions). This feature is **deferred to MVP** — the POC player
(N04/F35 + F36) plays the full page audio only.

## Dependencies

- Upstream features: N04/F35 (audio + rAF loop), N04/F36 (player state
  machine), N02/F22 (`ReadingPlan` block boundaries).
- Adapter ports consumed: none — consumer surface.
- External services: browser audio only.

## Interfaces

- DE-01: blockBoundaryUI — per-block play button rendered adjacent to each
  block region in the page image (ref: HLD-§3.1/Frontend).
- DE-02: blockAudioSegment — audio sub-range player; seeks audio to
  block start time and pauses at block end time using the timings from
  N03/F30 audio.json (ref: HLD-§3.1/Frontend).

## Approach

TBD — fill via `@design-pipeline` when MVP player is scheduled. Key
design questions: whether block boundaries are derived from page.json
bboxes or from a dedicated block-timing layer in audio.json; how block
controls interact with F36's global state machine.

## Design Elements

- DE-01: blockBoundaryUI (ref: HLD-§3.1/Frontend)
- DE-02: blockAudioSegment (ref: HLD-§3.1/Frontend)

## Decisions

TBD — pending MVP design cycle.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Per-block controls | Not in POC scope | PLAN-POC.md: F34 deferred MVP |

## HLD Open Questions

- Block boundary definition: bbox-derived vs audio-timing-derived — TBD at MVP design.
- Interaction with F36 global state machine — TBD.

## Risks

TBD — assessed at MVP design time.

## Out of Scope

- POC: all per-block control logic deferred.
- MVP: multi-page block navigation deferred post-MVP.
