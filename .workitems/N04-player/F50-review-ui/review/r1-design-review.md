# Design Review R1 — N04/F50 Review UI

**Reviewer:** Design self-review (inline R1)
**Date:** 2026-05-01
**Feature:** N04/F50 Review UI
**Artifacts reviewed:** user_stories.md, design.md, tasks.md, traceability.yaml, ADR-032

---

## Traceability Check

### Every US has ≥1 task

| User Story | Tasks |
|------------|-------|
| US-01 (4-button controls) | T-01 |
| US-02 (centered scan view) | T-02, T-14 |
| US-03 (inspector sidebar) | T-03, T-04, T-05, T-06, T-07, T-08 |
| US-04 (version navigator) | T-09, T-10 |
| US-05 (reviewer notes) | T-11, T-12 |

Result: PASS — all 5 user stories have at least one task.

### Every DE has ≥1 task

| Design Element | Tasks |
|----------------|-------|
| DE-01 (control wiring) | T-01 |
| DE-02 (centered layout) | T-02 |
| DE-03 (inspector sidebar) | T-03, T-04, T-05, T-06, T-07, T-13, T-14 |
| DE-04 (version navigator) | T-10 |
| DE-05 (notes persistence) | T-11, T-12 |
| DE-06 (OCR word sync) | T-08 |
| DE-07 (run_demo.py extension) | T-09 |

Result: PASS — all 7 design elements have at least one task.

### No task >2h

| Task | Estimate |
|------|----------|
| T-01 | 1h |
| T-02 | 0.5h |
| T-03 | 1h |
| T-04 | 1h |
| T-05 | 1h |
| T-06 | 0.5h |
| T-07 | 0.5h |
| T-08 | 1h |
| T-09 | 1h |
| T-10 | 1.5h |
| T-11 | 1h |
| T-12 | 0.5h |
| T-13 | 2h |
| T-14 | 0.5h |

Result: PASS — T-13 is exactly 2h (boundary is ≤2h). No task exceeds 2h.

Total estimated effort: **13.5h**

---

## Findings

### HIGH — T-09 test_file placement

**Finding:** T-09 routes to `tests/unit/test_pipeline.py` (Python), while all
other player tasks route to `player/test/inspector.spec.js` (Vitest/JS). This is
correct because `run_demo.py` is a Python file, but the split means the CI pipeline
must run both `pytest` and `vitest` for this feature. The tasks.md already calls
this out; ensure the Makefile / CI config includes both runners.

**Severity:** HIGH (workflow risk — missed runner = undetected regression)
**Action required:** Confirm CI runs both `pytest` and `vitest` before marking T-09 done.
**Blocks approval:** No — this is a pre-existing CI configuration concern, not a design gap.

### MEDIUM — DE-04 / T-09 fallback when drafts/ is empty

**Finding:** `GET /api/versions` reads `drafts/`. If `drafts/` does not exist or is
empty the endpoint must return `[]` (not 500). The design.md `_serve_versions()` sketch
does not make this explicit.

**Severity:** MEDIUM (robustness gap)
**Action required:** Add a guard in T-09 hints: if `drafts/` is absent return `[]`; log a
warning. Implementer should note this before starting T-09.

### LOW — Responsive version-nav spec is CSS-only without JS fallback

**Finding:** T-14 mentions a `<select>` fallback for `#version-nav` on narrow viewports
"via CSS + JS fallback". The design.md describes CSS collapse only. If CSS alone cannot
transform a `<nav><ul>` into a `<select>`, JS is required to swap the element. This
should be clarified before TDD starts on T-14.

**Severity:** LOW (implementation ambiguity, not a design gap)
**Action required:** Decide at TDD time: either a CSS-only `appearance` trick (simpler) or
a JS element swap (more accessible). Not a blocker for design approval.

### INFORMATIONAL — inspector.js cyclomatic complexity watch

`loadInspector(pageJson, audioJson)` touches 4 tabs + notes restoration. If implemented
as a single function it risks CC > 5. Recommend splitting into `_populateOcr`,
`_populateNlp`, `_populateNakdan`, `_populateVoice` helpers, each CC ≤ 2, with
`loadInspector` as the orchestrator (CC = 2: one call per helper + notes restore).

---

## Summary

| Severity | Count | Blocking |
|----------|-------|---------|
| Critical | 0 | — |
| High | 1 | No |
| Medium | 1 | No |
| Low | 1 | No |
| Informational | 1 | No |

No Critical concerns. All High/Medium findings are advisory and addressed by
implementation-time guards or CI configuration — they do not require design
document changes.

---

## Verdict

**APPROVED**

The design is consistent, all traceability checks pass, no task exceeds 2h, and
no Critical findings were identified. Proceed to TDD (`/tdd` router → T-01).
