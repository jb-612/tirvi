---
feature_id: N04/F37
feature_type: ui
status: designed
hld_refs:
  - HLD-§3.1/Frontend
prd_refs:
  - "PRD §6.6 — Player controls"
adr_refs: []
biz_corpus_e_id: E09-F05
gate: deferred_mvp   # not scheduled for POC; activate when MVP player begins
---

# Feature: Spell-Word (Letter-by-Letter Playback on Demand)

## Overview

Spell-word allows a student to tap or click any highlighted word during
playback to hear that word read letter-by-letter (or syllable-by-syllable)
in Hebrew. The player pauses the main audio, synthesizes a per-letter
pronunciation sequence via the existing TTS pipeline, plays it, and then
resumes. This feature is **deferred to MVP** — the POC player (N04/F35 +
F36) has no word-tap interaction.

## Dependencies

- Upstream features: N04/F35 (word marker, active mark_id), N04/F36
  (player state machine — extend with `spelling` state), N02/F22
  (word text from ReadingPlan), N03/F26 (TTS synthesis — reuse for letter
  sequence).
- Adapter ports consumed: TTS synthesis port (from N03).
- External services: Cloud TTS (or Wavenet) for letter synthesis; may use
  client-side Web Speech API as a lighter POC alternative.

## Interfaces

- DE-01: wordTapHandler — click/tap listener on the marker overlay during
  playback; captures the current `mark_id` and dispatches `spell` event
  to the state machine (ref: HLD-§3.1/Frontend).
- DE-02: letterSequenceSynth — decomposes Hebrew word text into letters or
  phoneme units and requests TTS synthesis for each; plays the sequence
  sequentially; resumes main audio on completion (ref: HLD-§3.1/Frontend).

## Approach

TBD — fill via `@design-pipeline` when MVP player is scheduled. Key
design questions: whether letter synthesis is pre-generated at pipeline
time or on-demand via client-side Web Speech API; interaction with F36's
state machine (new `spelling` state vs. `paused` sub-state); Hebrew
letter naming convention (אָלֶף vs. א sound only).

## Design Elements

- DE-01: wordTapHandler (ref: HLD-§3.1/Frontend)
- DE-02: letterSequenceSynth (ref: HLD-§3.1/Frontend)

## Decisions

TBD — pending MVP design cycle.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| Spell-word | Not in POC scope | PLAN-POC.md: F37 deferred MVP |

## HLD Open Questions

- Hebrew letter naming: phoneme only vs. letter name (אָלֶף) — TBD at MVP.
- Web Speech API vs. Cloud TTS for letter sequence — TBD at MVP.
- State machine extension (`spelling` state) — must coordinate with F36.

## Risks

TBD — assessed at MVP design time. Primary risk: Hebrew diacritics affect
letter pronunciation; letter synthesis without nikud may mispronounce.

## Out of Scope

- POC: spell-word entirely deferred.
- MVP: sentence-level replay (covered by F34 per-block repeat, if scoped).
