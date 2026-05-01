# Design Review R1 — N04/F38 WCAG 2.1 AA Conformance Audit (Deferred MVP)

**Feature:** N04/F38 — WCAG 2.1 AA conformance audit and remediation
**Date:** 2026-05-01
**Status:** R1 complete — approved as deferred MVP stub

---

## Scope Note

F38 is **deferred MVP** with a stub design. The POC ships only a basic
accessibility floor (F35-DE-06, F36-DE-06). No Critical or High findings
are raised for a stub. This review validates the stub and flags what must
be resolved before the audit runs.

---

## Finding Index

| ID | Severity | Reviewer | Title |
|----|----------|----------|-------|
| C1 | Low | U | Hebrew RTL success criteria are not covered by standard axe-core rules |
| C2 | Low | A | F38 must run after all player features are complete — sequencing risk |

---

## Finding Detail

### C1 — Low — Hebrew RTL not covered by standard axe-core

**Reviewer:** UX / Accessibility (U)

WCAG 2.1 SC 1.3.2 (Meaningful Sequence) and SC 1.3.4 (Orientation) have
Hebrew-specific failure modes (RTL bidi algorithm, mixed LTR/RTL content in
exam questions) that axe-core does not test. Manual screen-reader verification
with NVDA + a Hebrew TTS voice is required. The MVP designer must plan for
at least one manual testing session, not just the automated pipeline.

### C2 — Low — Sequencing: F38 is the last feature in N04

**Reviewer:** Architecture (A)

F38 explicitly depends on N04/F35, F36, F33, and F34 all being implemented.
F34 is also deferred MVP. This means F38 cannot begin until all four
upstream features are complete. The MVP project plan must account for this
at scheduling time.

---

## Summary Table

| ID | Severity | Action |
|----|----------|--------|
| C1 | Low | Plan manual RTL screen-reader session alongside automated audit |
| C2 | Low | Note F38 sequencing constraint in MVP project plan |

**R1 verdict:** Approved as deferred MVP stub. No revision needed now.
