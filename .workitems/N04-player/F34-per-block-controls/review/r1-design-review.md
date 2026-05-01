# Design Review R1 — N04/F34 Per-Block Playback Controls (Deferred MVP)

**Feature:** N04/F34 — Per-block playback controls
**Date:** 2026-05-01
**Status:** R1 complete — approved as deferred MVP stub

---

## Scope Note

F34 is **deferred MVP** with a stub design. No Critical or High findings
are raised for a stub — the design intentionally defers detail to the MVP
design cycle. This review validates the stub is well-formed and identifies
what must be resolved before TDD.

---

## Finding Index

| ID | Severity | Reviewer | Title |
|----|----------|----------|-------|
| C1 | Low | A | Block boundary definition is unresolved; must be addressed before MVP design |
| C2 | Low | H | F36 state machine interaction is unspecified |

---

## Finding Detail

### C1 — Low — Block boundary definition is unresolved

**Reviewer:** Architecture (A)

DE-02 refers to block start/end times derived from the timings in
`audio.json`. However `audio.json` currently has per-word marks only
(`mark_id`, `start_s`, `end_s`). Block boundaries would require either
(a) a new `blocks` key in `audio.json` from N03/F30, or (b) deriving block
boundaries from the `ReadingPlan` block partition in N02/F22 (which has
block metadata). Neither approach is committed to in the stub design.

This is expected for a deferred stub but must be the first question answered
when the MVP design cycle begins.

### C2 — Low — F36 state machine interaction unspecified

**Reviewer:** HLD Compliance (H)

The per-block play button creates a new event source not covered by F36's
`PlayerState` machine (`idle/playing/paused/ended`). Either F36 must be
extended with block-play events, or per-block controls operate as a parallel
controller that reuses the same audio element. The design correctly defers
this, but the MVP designer must read F36's design before F34 design begins.

---

## Summary Table

| ID | Severity | Action |
|----|----------|--------|
| C1 | Low | Resolve block boundary source at MVP design time |
| C2 | Low | Coordinate with F36 state machine design at MVP design time |

**R1 verdict:** Approved as deferred MVP stub. No revision needed now.
