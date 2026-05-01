# Design Review R2 — Adversary Challenge — N04/F35 Word-Sync Highlight

**Feature:** N04/F35 — Word-sync highlight (vanilla HTML POC)
**Round:** R2 adversary challenge + synthesis
**Date:** 2026-05-01
**Status:** R2 complete — approved with conditions

---

## Adversary Position

The adversary challenges the adequacy of R1 revisions and probes whether
residual risks are correctly classified.

---

### Challenge A — C1 resolution: "Jest via npm test" is a build-step violation

**Challenge:** R1 requested a JS test strategy decision. If the chosen
resolution is "Jest/Vitest co-located in `player/test/`", that introduces
a `package.json` and `node_modules/` at `player/` — a new dev dependency
that unlocks a new code path (per workflow.md scaffolding disqualifiers). The
workflow rule states this requires the full design + TDD pipeline, not
scaffolding classification. The design has not accounted for this dependency
in its task breakdown.

**Synthesis:** The adversary is correct that a `package.json` addition crosses
the scaffolding disqualifier threshold. However, T-01 through T-03 are already
marked implemented, meaning the test infrastructure decision has been made in
practice even if not documented. The design should retroactively document
the chosen runner (whatever was used for T-01..T-03) and note that the
`player/package.json` is part of T-01's deliverable, already complete.
**Resolution:** Accepted with condition — design.md must name the runner
actually used for the passing tests; no new task needed since T-01 is done.

---

### Challenge B — C2 resolution: helper extraction may not be sufficient

**Challenge:** R1 proposed extracting `shouldUpdateMarker` and
`applyMotionPreference` as pure helpers to keep the rAF callback at CC ≤ 3.
The adversary notes that `lookupWord` is called inside the callback and may
itself reach CC 3 (null check, boundary guard, binary search loop). If the
binary search uses a `while` loop with two inner conditions, it is CC 4 on
its own. Composing these — rAF callback calls `lookupWord` which calls into
the binary search — keeps each individual function under CC 5, but if the
binary search is ever inlined back into the rAF callback the combined CC
would reach 7.

**Synthesis:** The concern is valid for the future MVP refactor but not for
the current design, which already separates `lookupWord` into `timing.js`
(its own file, T-04). The ADR-023 vanilla-JS constraint makes inlining
unlikely during POC. CC monitoring via the `check-complexity.sh` hook
catches any regression at commit time.
**Resolution:** Finding does not require further design revision; the
`check-complexity.sh` hook is the enforcement mechanism.

---

### Challenge C — C3 is misclassified as Medium; should be High for Hebrew exams

**Challenge:** Hebrew exam words with nikud frequently have durations of
0.07–0.12 s (short function words like ה-/ו-). A 22 ms Safari floor on
`currentTime` means a 15–30 % chance of the wrong word being highlighted
on those tokens. In an accessibility product where word-sync is the primary
accommodation, this is not a "Low/Medium" cosmetic issue — it is a core
product flaw for Safari users.

**Synthesis:** The adversary's severity argument is strong for the MVP, but
the design explicitly scopes this as a POC with manual testing. The risk
entry added per C3 is the correct artifact for communicating this to the MVP
designer. Reclassification from Medium to High-for-POC would be over-indexing
on a risk that is correctly deferred. The risk entry must, however, explicitly
call out Hebrew short-word tokens as the primary failure mode (not just
"short words ≤ 0.1 s").
**Resolution:** Design.md risk entry to be updated to: "Safari currentTime
granularity ~22 ms — may cause marker desync on Hebrew short-word tokens
(ה-, ו-, ש-) with duration < 0.1 s; measured manually; deferred to MVP."

---

### Challenge D — C4 partial: matchMedia mock is not enough to test the CSS path

**Challenge:** Even with `matchMedia` mocked to `{matches: true}`, the test
can only assert that `element.classList.contains("no-animation")` is true.
It cannot assert that the CSS transition is actually suppressed, because jsdom
does not compute styles. The test gives false confidence: the class is added
but the CSS rule in `index.html`'s `<style>` block could be absent and the
test would still pass.

**Synthesis:** The adversary is correct that jsdom cannot test computed styles.
T-06 should additionally include a smoke assertion that the `.no-animation`
CSS rule exists in the style block (or a separate stylesheet), using a simple
string search over the HTML source. This is a low-effort addition to the
test hints.
**Resolution:** T-06 hints to be updated: "Additionally assert `.no-animation`
rule exists in HTML `<style>` block via `innerHTML.includes` or equivalent."

---

## Net Revisions Required After R2

| Challenge | Finding ref | Action | Owner |
|-----------|-------------|--------|-------|
| A | C1 | Name actual runner in design.md; assert player/package.json is T-01 deliverable | Design author |
| B | C2 | No revision needed; hook handles enforcement | — |
| C | C3 | Update risk entry with Hebrew short-word token specifics | Design author |
| D | C4 | Add CSS-rule existence assertion to T-06 hints | Design author |

---

## R2 Synthesis Verdict

**Approved with four targeted revisions** (all in `design.md` / task hints;
no structural redesign required). F35 is cleared for TDD on tasks T-04,
T-05, T-06 once revisions are applied. T-01, T-02, T-03 are already
implemented and are not affected.

Residual risk: Safari timing granularity on short Hebrew tokens — accepted
for POC scope; tracked in design.md §Risks. MVP owner must revisit before
shipping to real students.
