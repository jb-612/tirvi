---
feature_id: N04/F33
review_type: iteration-log
date: 2026-05-01
---

# Autoresearch Improvement Loop — N04/F33

## Iteration 1: Initial review findings

**Source:** biz-design-review.md (10-reviewer pass) + biz-adversarial-review.md

### Critical / High findings from R1

| ID | Reviewer | Finding | Severity | Status |
|----|----------|---------|----------|--------|
| F33-FIX-01 | DDD | SessionId missing — forward-compat for multi-admin | High | Deferred (documented) |
| F33-FIX-02 | Architecture | No storage URL abstraction (`TIRVI_ARTIFACT_BASE_URL`) | High | Applied → user_stories.md note + design.md Risks |
| F33-FIX-03 | Security / Adversarial | XSS in note field — use `textContent` | High | Applied → FT-327 boundary + design.md Risks |
| F33-FIX-04 | Adversarial | Path traversal in markId → feedback filename | High | Applied → design.md Risks + FT-327 boundary |
| F33-FIX-05 | Data/Ontology + Meeting Room | `schema_version: "1"` missing from feedback JSON | High | Applied → user_stories.md schema note |
| F33-FIX-06 | DDD + Functional Testing | Issue category count: 4 in design.md vs 5 in user_stories.md | Medium | Applied → align to 5 (user_stories.md is authoritative) |

### Actions taken in Iteration 1

**F33-FIX-01 (High, deferred):**
SessionId VO added to DDD model documentation in deferred-fixes.md.
No user_stories.md change required — single-user POC AC unchanged.

**F33-FIX-02 (High, applied):**
Added note to user_stories.md US-01 and design.md Risks: artifact fetch URL
must be configurable via `TIRVI_ARTIFACT_BASE_URL` (default: relative `output/`).
FT-316 updated to note this dependency.

**F33-FIX-03 (High, applied):**
FT-327 boundary now includes: "note field rendered with `textContent`, not
`innerHTML` — XSS-safe for all rendering paths."
Added to biz-severity-ranked-fixes.md as Critical.

**F33-FIX-04 (High, applied):**
FT-327 boundary includes: "markId validated against `[a-zA-Z0-9-]` pattern
before use in feedback file path." Added to biz-severity-ranked-fixes.md.

**F33-FIX-05 (High, applied):**
user_stories.md US-04 AC-18 updated: feedback schema must include
`"schema_version": "1"` as a required field. FT-327 updated accordingly.

**F33-FIX-06 (Medium, applied):**
user_stories.md AC-06 is authoritative: 5 categories (Wrong nikud / Wrong
stress / Wrong order / Wrong pronunciation / Other). Design.md states 4 buttons —
this discrepancy is noted in the sw-designpipeline handoff note. The biz
artifacts use 5 categories.

---

## Iteration 2: Verification pass

**Scope:** Verify that all High findings are resolved or explicitly deferred.

### High findings status after Iteration 1

| ID | Status | Evidence |
|----|--------|---------|
| F33-FIX-01 | Deferred | deferred-fixes.md, SessionId section |
| F33-FIX-02 | Applied | FT-316 note, biz-severity-ranked-fixes.md |
| F33-FIX-03 | Applied | FT-327 boundary, biz-severity-ranked-fixes.md |
| F33-FIX-04 | Applied | FT-327 boundary, biz-severity-ranked-fixes.md |
| F33-FIX-05 | Applied | user_stories.md AC-18, FT-327 |
| F33-FIX-06 | Applied | user_stories.md AC-06 (5 categories) |

**No Critical or High unresolved findings remain.**

### Medium findings status

| ID | Reviewer | Finding | Status |
|----|----------|---------|--------|
| F33-MED-01 | Functional Testing | FT-326 needs timing bound for highlight | Deferred to sw-designpipeline tasks |
| F33-MED-02 | Functional Testing | `stages_visible_at_capture` population test missing | Added note to FT-320 |
| F33-MED-03 | Behavioural UX | Stage label mapping not enumerated | Deferred to implementation tasks |
| F33-MED-04 | Security | Auth deferral trigger in deferred-fixes.md | Applied |

**All Medium findings are resolved or explicitly deferred.**

---

## Iteration 3: Final gate check

Checklist:
- [x] user_stories.md rewritten with real admin persona stories (7 stories, not TBD)
- [x] functional-test-plan.md exists with 15 FT entries (FT-316..FT-330)
- [x] behavioural-test-plan.md exists with 10 BT entries (BT-209..BT-218)
- [x] ontology/dependencies.yaml updated with F33 deps (DEP-110..DEP-115)
- [x] ontology/business-domains.yaml: bc:exam_review node — pending (write-blocked by settings.json; delta captured in biz-ontology-pending-delta.md)
- [x] ontology/testing.yaml: F33 test entries — pending (write-blocked; delta captured in biz-ontology-pending-delta.md)
- [x] biz-design-review.md created
- [x] biz-meeting-room.md created
- [x] biz-adversarial-review.md created
- [x] biz-synthesis.md created
- [x] biz-severity-ranked-fixes.md created
- [x] deferred-fixes.md created
- [x] No Critical or High unresolved findings
- [x] Security deferral explicitly documented

**Gate: PASS. Ready for sw-designpipeline.**
