# Design Review R1 — N04/F37 Spell-Word (Deferred MVP)

**Feature:** N04/F37 — Spell-word (letter-by-letter playback on demand)
**Date:** 2026-05-01
**Status:** R1 complete — approved as deferred MVP stub

---

## Scope Note

F37 is **deferred MVP** with a stub design. No Critical or High findings
are raised for a stub. This review validates the stub is well-formed and
identifies what must be resolved before TDD.

---

## Finding Index

| ID | Severity | Reviewer | Title |
|----|----------|----------|-------|
| C1 | Low | A | Hebrew letter naming convention unresolved (phoneme vs. letter name) |
| C2 | Low | H | F36 state machine extension creates inter-feature dependency |

---

## Finding Detail

### C1 — Low — Hebrew letter naming convention

**Reviewer:** Architecture (A)

Spelling a Hebrew word letter-by-letter requires a decision on whether the
TTS reads the letter's phoneme sound (e.g., "b" for ב) or its traditional
Hebrew name (e.g., "בֵּית"). For students with reading difficulties, letter
names are more likely to be recognizable, but synthesizing letter names
requires a lookup table mapping Unicode Hebrew codepoints to nikud-annotated
names. This table does not currently exist in the codebase. The design
correctly defers this, but it should be the first design decision when
F37's MVP cycle begins.

### C2 — Low — F36 state machine requires extension

**Reviewer:** HLD Compliance (H)

The `spelling` state (described in design.md §Approach) is not in F36's
current state machine (`idle/playing/paused/ended`). Adding it at MVP
will require a revision to F36 — a feature that will already be in
production by then. The MVP designer must plan for a coordinated change to
F36's `nextState` function and its test suite.

---

## Summary Table

| ID | Severity | Action |
|----|----------|--------|
| C1 | Low | Resolve Hebrew letter naming at MVP design time |
| C2 | Low | Plan F36 state machine extension as a coordinated task at MVP |

**R1 verdict:** Approved as deferred MVP stub. No revision needed now.
