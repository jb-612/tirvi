---
feature_id: N04/F33
review_type: deferred-fixes
date: 2026-05-01
---

# Deferred Fixes — N04/F33 Exam Review Portal

This file records findings that are intentionally NOT fixed now, with the
reason and re-evaluation trigger for each.

---

## DEFERRED-01: Authentication / Security — Intentional, Pre-Approved

**Source:** biz-design-review.md Reviewer 7, biz-adversarial-review.md Challenge 4
**Finding:** The portal has no authentication. Any network-reachable client can
browse pipeline artifacts and read feedback annotations.
**Why deferred:** Explicitly approved by the user. The design brief states:
"Security/auth is explicitly deferred as a separate NFR — build it functionally
open first."
**Scope of deferral:** Localhost POC only. The portal is served by
`python -m http.server` on a local port with no network exposure.

**Re-evaluation trigger:**
- Before any deployment that exposes the portal on a network reachable by
  more than one machine (including staging VMs).
- Minimum mitigation for staging: HTTP basic auth via reverse proxy (nginx).
- Full auth NFR: tracked separately; see PRD §4 Non-goals and HLD §11.

**Owner:** engineering team lead, at staging-deployment planning.

---

## DEFERRED-02: SessionId VO for Multi-Admin Forward-Compatibility

**Source:** biz-design-review.md Reviewer 2
**Finding:** `ReviewSession` has no `SessionId` — only `RunId`. Two concurrent
admins produce overlapping feedback files with no attribution.
**Why deferred:** Single-user POC assumption. No concurrent review planned.
**Re-eval trigger:** Multi-admin deployment. Add `session_id` (UUID) to feedback
JSON at schema_version "2". F48 must group by session_id.

---

## DEFERRED-03: Concurrent Review Collision Handling

**Source:** biz-adversarial-review.md Challenge 2
**Finding:** Two concurrent users produce duplicate markId entries in F48.
**Why deferred:** Single-user POC assumption.
**Re-eval trigger:** Same as DEFERRED-02. F48 must deduplicate by latest ts.

---

## DEFERRED-04: Stage Label Enumeration Mapping

**Source:** biz-design-review.md Reviewer 4
**Finding:** BT-211 relies on "plain language labels" but no mapping table
(`06-diacritize` → "Diacritized text / ניקוד") is defined in biz artifacts.
**Why deferred:** Implementation detail. ACs say labels must be human-readable;
exact mapping is a UX decision for sw-designpipeline tasks.

---

## DEFERRED-05: FT-326 Highlight Timing Bound

**Source:** biz-design-review.md Reviewer 3
**Finding:** FT-326 asserts "continues working" without a measurable bound.
**Why deferred:** Bound (≤ 80 ms) is already in FT-244 (E09-F03). FT-326
should link to FT-244 rather than duplicate it. Updated in functional-test-plan.part-2.md.

---

## DEFERRED-06: Ontology YAML Updates for bc:exam_review and Testing Entries

**Source:** Stage 4 and Stage 7 of biz-functional-design skill execution
**Finding:** `ontology/business-domains.yaml` and `ontology/testing.yaml` require
new entries for F33 (bc:exam_review bounded context, F33 test range entries).
These files are write-blocked by `settings.json` deny rules for the current
branch.

**Pending delta** is captured in:
`.workitems/N04-player/F33-side-by-side-viewer/review/biz-ontology-pending-delta.md`

**Re-evaluation trigger:** The team lead or a privileged session should apply
the pending delta to ontology/business-domains.yaml and ontology/testing.yaml
when the branch permissions are updated. The delta is idempotent and additive.

**ontology/dependencies.yaml** was successfully updated with DEP-110..DEP-115.

---

## Summary Table

| ID | Deferral | Trigger | Risk if Not Addressed |
|----|----------|---------|----------------------|
| DEFERRED-01 | Auth/security | Before network deployment | Any user on network reads artifacts and annotations |
| DEFERRED-02 | SessionId VO | Multi-admin use case | No reviewer attribution in feedback |
| DEFERRED-03 | Concurrent collision | Multi-admin use case | Duplicate feedback confuses F48 aggregator |
| DEFERRED-04 | Stage label mapping | sw-designpipeline tasks | BT-211 cannot be verified objectively |
| DEFERRED-05 | FT-326 timing bound | TDD for F35 integration | Highlight regression undetected |
| DEFERRED-06 | Ontology YAML writes | Privileged session / branch | bc:exam_review missing from project graph |
