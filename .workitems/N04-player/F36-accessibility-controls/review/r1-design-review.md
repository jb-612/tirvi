# Design Review R1 — N04/F36 Accessibility Controls (4-button POC)

**Feature:** N04/F36 — Accessibility controls (4-button POC)
**Reviewers:** Architecture (A), Code Quality / Security (Q), Test Coverage (T),
  HLD Compliance (H), UX / Accessibility (U), Product (P)
**Date:** 2026-05-01
**Status:** R1 complete — revisions requested

---

## Finding Index

| ID | Severity | Reviewer | Title |
|----|----------|----------|-------|
| C1 | High | A | State machine pure-function correctness: `ended → Play` transition needs explicit reset |
| C2 | Medium | U | ARIA label language: Hebrew-first vs English-first creates ambiguity for AT users |
| C3 | Medium | T | T-01 done; T-02–T-06 pending — test coverage gap risk before TDD resumes |
| C4 | Low | Q | Continue/Reset disable logic is asymmetric in `idle` vs `ended` states |

---

## Finding Detail

### C1 — High — State machine: `ended → Play` transition needs explicit currentTime reset

**Reviewer:** Architecture (A)

The design specifies `ended → Play → playing (from start)` as "same as
idle." However DE-03 describes the Play handler as calling `audio.play()`
only. When `<audio>` has reached the end and `currentTime === duration`,
calling `audio.play()` without first resetting `currentTime = 0` leaves the
audio at end-of-file; playback may fire an immediate `ended` event again
without producing audible output in some browsers (Firefox, Safari).

The pure-function `nextState` is correct (it does not have side effects), but
the side-effect dispatch table in `Controls.bind` must map the `ended + play`
transition to `currentTime = 0; audio.play()` — the same sequence as `reset`.
The design's DE-03 hints say "audio.play()" only for the Play button, without
noting this special case.

**Requested revision:** Add a note to DE-03: "When entering `playing` from
`ended` (not from `idle` or `paused`), prepend `audio.currentTime = 0` to
the side-effect sequence." Update T-03 hints to test the `ended + play`
transition explicitly.

---

### C2 — Medium — ARIA label language: Hebrew-first ordering for screen readers

**Reviewer:** UX / Accessibility (U)

DE-01 and DE-06 specify `aria-label="Play / נגן"` — English label first,
Hebrew second. Hebrew-speaking students using a screen reader (NVDA,
VoiceOver, Orca) configured for Hebrew will have the TTS voice announce the
English word "Play" before switching to Hebrew pronunciation rules for "נגן".
This creates a jarring bilingual announcement. The better pattern for a
Hebrew-primary product is `aria-label="נגן / Play"` (Hebrew first), which
reads naturally for the primary user and still surfaces the English term for
secondary users.

The biz corpus (E09-F04) targeted Hebrew-speaking students with reading
accommodations (personas P01, P02) as the primary audience.

**Requested revision:** Reverse label order to Hebrew-first: `aria-label="נגן
/ Play"`, `aria-label="השהה / Pause"`, `aria-label="המשך / Continue"`,
`aria-label="אפס / Reset"`. Update DE-01 and DE-06 accordingly.

---

### C3 — Medium — T-01 done / T-02–T-06 pending: design must not block TDD restart

**Reviewer:** Test Coverage (T)

The tasks.md shows T-01 as implemented (`[x]`) and T-02 through T-06 as
pending. The design review of T-01 (button DOM scaffold) has been bypassed
by completing implementation before the design review cycle completed. While
the POC pragmatics make this acceptable, the risk is that any R1/R2 revisions
affecting DE-01 or DE-06 (ARIA labels — see C2 above) require a retroactive
change to already-committed DOM.

More importantly: T-02 (pure state machine) has no dependencies in the DAG
(`T-01 → T-03 → T-04`, `T-02 → T-03 → T-04`), so TDD can restart on T-02
immediately after R2 approval without blocking on T-01 changes.

**Requested revision:** Design note to confirm that T-02 can be picked up
independently of T-01 ARIA revisions; add a note that T-01's ARIA label
update (per C2) is a minor DOM change that does not alter the test scaffold.

---

### C4 — Low — Enable/disable asymmetry: `idle` vs `ended` both show Play, but Continue visibility differs

**Reviewer:** Code Quality / Security (Q)

DE-04 specifies:
- `idle`: Play enabled, others disabled
- `ended`: Play + Reset enabled

The design also states "DE-04 hides Continue in `idle` / `ended`" — but the
Risks section notes "Continue button confuses users (vs Play)." If `ended`
shows Play and Reset but not Continue, that is consistent. However the hint
"only Play is shown" for `idle` implies Continue may be visually hidden (not
just disabled), while `ended` only disables Continue. This asymmetry — hidden
in one state, disabled in another — is not explicitly documented.

**Requested revision:** Clarify in DE-04 whether Continue is `display: none`
or `disabled` in `idle` state. Consistent behavior (`disabled` in both `idle`
and `ended`) is preferred for WCAG 4.1.2 (Name, Role, Value) — the element
should remain in the accessibility tree.

---

## Summary Table

| ID | Severity | Accept / Revise | Owner |
|----|----------|-----------------|-------|
| C1 | High | Revise: add `ended→play` currentTime=0 to DE-03 + T-03 hints | Design author |
| C2 | Medium | Revise: reverse ARIA label order to Hebrew-first in DE-01/DE-06 | Design author |
| C3 | Medium | Accept: note T-02 DAG independence in design; no structural change | Design author |
| C4 | Low | Revise: clarify `disabled` vs `display:none` for Continue in idle | Design author |

**R1 verdict:** One High finding requires revision before design is approved.
Proceed to R2 adversary challenge after revisions are applied.
