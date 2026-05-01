# Design Review R2 — Adversary Challenge — N04/F36 Accessibility Controls

**Feature:** N04/F36 — Accessibility controls (4-button POC)
**Round:** R2 adversary challenge + synthesis
**Date:** 2026-05-01
**Status:** R2 complete — approved with conditions

---

## Adversary Position

The adversary challenges whether the R1 revisions are sufficient and whether
any findings are misclassified in severity or scope.

---

### Challenge A — C1 resolution: adding `currentTime=0` to ended→play does not fix all browsers

**Challenge:** R1 proposed setting `audio.currentTime = 0` before `audio.play()`
in the `ended → play` transition. The adversary notes that on some browsers
(notably iOS Safari), setting `currentTime` on an ended `<audio>` element
before calling `play()` may throw a `NotSupportedError` if the element is
not in a "can-play" state. The fix is to use `audio.load()` first (which
resets the element to `HAVE_NOTHING` state), then `audio.play()`. However
`audio.load()` also clears any `src` set dynamically.

**Synthesis:** The adversary's Safari edge case is valid but applies to
mobile iOS, not the primary POC target (desktop browser for exam session).
The simpler `currentTime = 0; audio.play()` approach works on Chrome,
Firefox, and macOS Safari. The design note added per C1 should be accepted
as-is for POC; the `audio.load()` alternative is documented as a risk entry:
"iOS Safari `ended` → play may require `audio.load()` instead of
`currentTime=0`; deferred to MVP."
**Resolution:** C1 revision accepted; add iOS Safari caveat to §Risks.

---

### Challenge B — C2 resolution: Hebrew-first ARIA may break English AT configurations

**Challenge:** R1 proposed `aria-label="נגן / Play"` (Hebrew-first). The
adversary challenges this: a teaching assistant or invigilator using an
English AT configuration (NVDA on Windows in English mode) will hear "נגן"
announced with English phoneme rules, producing an incomprehensible
announcement before the recognizable "Play" word. The student using Hebrew
AT hears Hebrew correctly; the invigilator using English AT does not.

**Synthesis:** The adversary correctly identifies that a bilingual label
serves two audiences with different AT configurations. For a POC with a
single target user (Hebrew student), Hebrew-first is correct. The design
should acknowledge that `lang` attribute scoping on the button element
(`lang="he"`) allows AT to switch pronunciation engine correctly for the
Hebrew portion. This is additive to the ARIA label revision — not a
blocker. Add `lang="he"` to each button element in DE-01.
**Resolution:** C2 revision accepted; add `lang="he"` attribute on button
elements as an additional DE-01 note.

---

### Challenge C — C3 is under-classified: T-01 committed without review is a process violation

**Challenge:** The adversary argues that T-01 being implemented before R1
completion is not merely a "pragmatics" issue — it is a process violation
that should be logged. If DE-01 or DE-06 revisions require DOM changes, the
already-committed T-01 code must be amended, which introduces untested
intermediate states.

**Synthesis:** The adversary is technically correct per workflow.md §workflow
(TDD Build starts after User Gate). For the POC, the pragmatic override is
defensible: T-01 is a mechanical DOM scaffold (4 buttons + ARIA attributes)
with no business logic, and the HTML lint test provides sufficient coverage.
The ARIA label change from C2 is a string update — one-line diff. This
finding is correctly classified as Medium. The process note is accepted: the
commit message for the C2 ARIA fix should reference the R1 review finding
(`fix(N04/F36/T-01): ARIA label Hebrew-first per R1-C2`).
**Resolution:** No severity change; commit message convention added.

---

### Challenge D — C4 is misclassified as Low; WCAG 4.1.2 requires `disabled`, not hidden

**Challenge:** The adversary argues C4 should be High: hiding a button with
`display:none` removes it from the accessibility tree entirely, which means
AT users cannot discover its existence. A student who does not know Continue
exists (because they never saw it in idle state) may not think to look for
it after pausing. WCAG 4.1.2 (Name, Role, Value) requires that interactive
components remain in the tree with an accessible name. `display:none`
violates this for interactive controls.

**Synthesis:** The adversary correctly identifies the WCAG 4.1.2 implication.
However the risk is mitigated if `disabled` is used consistently (the
preferred approach from C4's revision request). The severity is upgraded from
Low to Medium because the WCAG violation would affect real screen-reader users
in the POC session. The revision from R1 — "use `disabled` in all states,
never `display:none`" — is the correct fix and must be treated as blocking
before TDD on T-04.
**Resolution:** Severity upgraded to Medium; T-04 must not begin until DE-04
explicitly specifies `disabled` (not hidden) for Continue in `idle`.

---

## Net Revisions Required After R2

| Challenge | Finding ref | Action | Owner |
|-----------|-------------|--------|-------|
| A | C1 | Add iOS Safari `audio.load()` caveat to §Risks | Design author |
| B | C2 | Add `lang="he"` attribute note to DE-01 | Design author |
| C | C3 | Accept; add commit message convention note | Design author |
| D | C4 | Upgrade severity to Medium; T-04 blocked until DE-04 specifies `disabled` | Design author |

---

## R2 Synthesis Verdict

**Approved with four targeted revisions** (all in `design.md` and task
hints; no structural redesign). F36 is cleared for TDD on tasks T-02 and
T-05 immediately (no DE dependencies on revised elements). T-03 and T-04
start after DE-03/DE-04 revisions are applied. T-01 ARIA fix is a one-line
amendment included in the next TDD cycle commit.

State machine design (DE-02, `nextState` pure function) is well-formed and
requires no revision. Cross-dependency with F35 (shared audio element, shared
palette tokens) is correctly captured in the design.
