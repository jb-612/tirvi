---
feature_id: N04/F33
review_type: severity-ranked-fixes
date: 2026-05-01
---

# Severity-Ranked Fixes — N04/F33 Exam Review Portal

Ordered by severity (Critical first), then by effort (simplest first within tier).
Fixes are either applied (to biz artifacts) or deferred (to design.md /
implementation tasks) as noted.

---

## Critical — Must apply before TDD

### FIX-01: XSS in note field — use textContent

**Severity:** Critical (security)
**Source:** biz-design-review.md Reviewer 9, biz-adversarial-review.md Challenge 5
**Fix:** When rendering annotation notes in the review list (US-07), the implementation
must use `element.textContent = note` not `element.innerHTML = note`.
**Applied to:** FT-327 boundary condition — "note field rendered with textContent,
not innerHTML". sw-designpipeline must add to design.md Risks table.
**Effort:** 1 line in implementation.

### FIX-02: markId path traversal validation

**Severity:** Critical (security)
**Source:** biz-design-review.md Reviewer 9 (Medium), biz-adversarial-review.md Challenge 5
**Fix:** The feedback server endpoint (or client-side file write) must validate
`markId` against the pattern `[a-zA-Z0-9-]+` before constructing the filename
`output/<N>/feedback/<markId>-<ts>.json`. A markId containing `../` would allow
path traversal.
**Applied to:** FT-327 boundary condition. sw-designpipeline must add to design.md
server endpoint spec.
**Effort:** 1 regex check.

### FIX-03: Add `schema_version: "1"` to feedback JSON schema

**Severity:** Critical (data forward-compatibility)
**Source:** biz-design-review.md Reviewer 6, biz-meeting-room.md Topic 3,
biz-adversarial-review.md Challenge 3
**Fix:** Add `"schema_version": "1"` as a required field in the feedback JSON
schema in design.md and user_stories.md AC-18.
**Applied to:** user_stories.md AC-18 now references `schema_version`. FT-327
validates presence. sw-designpipeline must update design.md feedback schema block.
**Effort:** 1 field addition.

---

## High — Required before sw-designpipeline handoff

### FIX-04: Align issue category count to 5

**Severity:** High (data consistency)
**Source:** biz-design-review.md Reviewer 2 and 6
**Fix:** user_stories.md AC-06 specifies 5 categories (Wrong nikud / Wrong stress /
Wrong order / Wrong pronunciation / Other). design.md currently lists 4 buttons
in DE-06. sw-designpipeline must align design.md to 5 categories.
**Applied to:** user_stories.md AC-06 is authoritative at 5. design.md fix is
sw-designpipeline's responsibility.
**Effort:** 1 button in UI implementation + enum value in feedback JSON.

### FIX-05: Storage URL abstraction (`TIRVI_ARTIFACT_BASE_URL`)

**Severity:** High (production-path blocker)
**Source:** biz-design-review.md Reviewer 5, biz-meeting-room.md Topic 1
**Fix:** `sidebar.js` and other JS modules must not hardcode `output/<N>/` as
the artifact base URL. A `TIRVI_ARTIFACT_BASE_URL` environment variable (or
config.js constant) must be the single origin. Default: `./output/` for POC;
override for GCS signed URL prefix in production.
**Applied to:** Note added to FT-316 (portal loads). sw-designpipeline must add
to design.md interfaces table (runner.js section).
**Effort:** 1 config constant + replace hardcoded paths.

---

## Medium — Address before TDD if possible

### FIX-06: SessionId VO for forward-compatibility
**Severity:** Medium | **Source:** biz-design-review.md Reviewer 2
**Fix:** Add `SessionId` VO to DDD model documentation for single-user POC.
**Disposition:** Deferred to deferred-fixes.md (DEFERRED-02). Not blocking.

### FIX-07: Auth deferral trigger documented
**Severity:** Medium | **Source:** biz-design-review.md Reviewer 7
**Fix:** deferred-fixes.md states: "Localhost only. HTTP basic auth before any
network deployment." Applied to deferred-fixes.md (DEFERRED-01).

### FIX-08: FT-326 highlight timing bound
**Severity:** Medium | **Source:** biz-design-review.md Reviewer 3
**Fix:** FT-326 updated to reference FT-244 (≤ 80 ms timing bound) not "correctly".
Applied to functional-test-plan.part-2.md FT-326.

### FIX-09: `stages_visible_at_capture` population test
**Severity:** Medium | **Source:** biz-design-review.md Reviewer 3
**Fix:** FT-320 note: array must contain only stages actually opened by admin.
Applied to functional-test-plan.md FT-320 note.

---

## Low — Polish; defer to implementation

- Stage label mapping enumeration (BT-211 — define `01-ocr` → "OCR words" table)
- Export filename colons on Windows (`T185500Z` format)
- `design.md` title update to "Exam Review Portal"
- BT-218 classification as SMOKE test
- FT-327 review for US-06 "demo-mode blocked" traceability note
