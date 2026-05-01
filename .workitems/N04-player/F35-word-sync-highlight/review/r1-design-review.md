# Design Review R1 — N04/F35 Word-Sync Highlight (Vanilla HTML POC)

**Feature:** N04/F35 — Word-sync highlight (vanilla HTML POC)
**Reviewers:** Architecture (A), Code Quality / Security (Q), Test Coverage (T),
  HLD Compliance (H), UX / Accessibility (U), Product (P)
**Date:** 2026-05-01
**Status:** R1 complete — revisions requested

---

## Finding Index

| ID | Severity | Reviewer | Title |
|----|----------|----------|-------|
| C1 | High | T | JS-in-Python test harness: jsdom strategy is unspecified |
| C2 | High | A | requestAnimationFrame loop cyclomatic complexity risk |
| C3 | Medium | U | Cross-browser `requestAnimationFrame` and audio timing precision |
| C4 | Medium | H | `prefers-reduced-motion` implementation is untested at DE-06 |
| C5 | Low | Q | Missing schema validation path for `page.json` degraded case |

---

## Finding Detail

### C1 — High — JS-in-Python test harness: jsdom strategy is unspecified

**Reviewer:** Test Coverage (T)

The design specifies that T-02 (timings loader), T-03 (rAF loop), T-04
(binary search), and T-05 (marker positioning) are tested from Python
(`tests/unit/test_*.py`). The hints acknowledge "jsdom-based test
exercises the JS module without browser" for T-02, but the mechanism is
never specified: jsdom runs in Node.js, not CPython. There are three
viable strategies — (a) a thin Python subprocess shim that runs
`node --experimental-vm-modules` against each JS module, (b) a
Playwright-headless fixture that boots a real browser, or (c) a full
Jest/Vitest suite in JavaScript that Python's CI script invokes via
`npm test`. None is committed to in `design.md`, `tasks.md`, or ADR-023.

Without a concrete test-runner decision, T-02..T-05 cannot achieve GREEN:
the TDD writer will either skip JS tests entirely (producing false
confidence) or invent a harness mid-cycle that is not reviewed.

**Requested revision:** State the chosen JS test strategy in `design.md`
§Approach DE-02 or in a new ADR; update T-02 hints to reference the
concrete runner. Acceptable to say "Jest via `npm test` co-located in
`player/test/`; Python CI calls `npm test` as a subprocess."

---

### C2 — High — requestAnimationFrame loop cyclomatic complexity risk

**Reviewer:** Architecture (A)

DE-03 describes the rAF callback as: read `audio.currentTime` → call
`lookupWord` → compare against cached `lastMarkId` → if changed, call
`positionMarker` → re-arm with `requestAnimationFrame`. If
`prefers-reduced-motion` is also checked inside the same callback (as DE-06
implies), and error-boundary logic (audio ended, null mark from lookupWord)
is inlined, the single callback function will reach cyclomatic complexity 6
or higher — breaching the project CC ≤ 5 rule.

The rAF callback is the hot path (60 fps); splitting it naively can add
indirection that hurts readability. The preferred pattern is: extract
`shouldUpdateMarker(currentTime, lastMarkId, timings) -> bool` and
`applyMotionPreference(marker, reducedMotion)` as pure helpers, leaving the
rAF callback itself at CC ≤ 3.

**Requested revision:** Add a design note to DE-03 specifying the callback's
internal structure and the two helper extractions; confirm CC budget.

---

### C3 — Medium — Cross-browser `requestAnimationFrame` and audio timing precision

**Reviewer:** UX / Accessibility (U)

The design claims "timing budget ≤ 80 ms (ASM10) measured manually for POC"
but the only risk entry is about the `drafts/<sha>/` directory not being
served. Cross-browser audio engine timing precision is a documented
real-world problem: Safari on macOS reports `audio.currentTime` with
~22 ms granularity; Chrome is ~1 ms. At 80 ms token budgets this may not
matter for Hebrew text, but it will produce visible marker skips on short
words (≤ 0.1 s duration) in Safari.

For the POC the risk is acceptable, but it should be documented in
`design.md §Risks` so the MVP migration to React does not inherit an
undocumented timing assumption.

**Requested revision:** Add a `Risks` entry: "Safari `currentTime` granularity
~22 ms — may cause single-frame marker desync on short words; acceptable
for POC; revisit at MVP."

---

### C4 — Medium — `prefers-reduced-motion` implementation is untested at DE-06

**Reviewer:** HLD Compliance (H)

DE-06 specifies that `window.matchMedia("(prefers-reduced-motion: reduce)")
.matches` suppresses CSS transitions. T-06 is assigned test file
`tests/unit/test_a11y_player.py`. However the jsdom strategy (C1 above)
is unknown, and even with jsdom, `window.matchMedia` is a stub that always
returns `false` unless explicitly mocked per the JSDOM FAQ. The design
does not call this out.

If T-06 tests the `matchMedia` branch without explicitly mocking the media
query result, the test will always pass the non-reduced-motion path and
provide no coverage for the reduced-motion branch — a silent false positive.

**Requested revision:** T-06 hints should note: "mock `window.matchMedia`
with both `matches: true` and `matches: false` to exercise both branches."

---

### C5 — Low — Missing schema validation path for `page.json` degraded case

**Reviewer:** Code Quality / Security (Q)

Post-review addition C2 in `design.md` (the degraded path note) says:
"`page.json` missing fails loud." However the schema validation path for
a *malformed* `page.json` (present but invalid against
`docs/schemas/page.schema.json`) is not specified: does it fail loud with
the same error path, silently skip rendering, or emit a banner like the
`audio.json` degraded case? The inconsistency is small but could produce
a confusing UX in debugging sessions.

**Requested revision:** Add one line to DE-02 degraded path: "malformed
`page.json` (schema validation failure) follows the same loud-fail path as
missing `page.json`."

---

## Summary Table

| ID | Severity | Accept / Revise | Owner |
|----|----------|-----------------|-------|
| C1 | High | Revise: specify JS test runner in design.md or new ADR | Design author |
| C2 | High | Revise: document CC budget + helper extraction in DE-03 | Design author |
| C3 | Medium | Revise: add Safari timing risk entry | Design author |
| C4 | Medium | Revise: T-06 hints must mock matchMedia both branches | Design author |
| C5 | Low | Revise: clarify malformed page.json failure mode | Design author |

**R1 verdict:** Two High findings require revision before design is approved.
Proceed to R2 adversary challenge after revisions are applied.
