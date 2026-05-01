---
feature_id: N04/F33
review_type: biz-design
round: R1
reviewers: 10 (parallel)
part: 1-of-2
continued_in: biz-design-review.part-2.md
date: 2026-05-01
---

# Business Design Review — N04/F33 Exam Review Portal (Part 1 of 2)

Reviewers 1–5 here. Reviewers 6–10 and Team Lead Synthesis in part 2.

## Reviewer 1: Product Strategy

**Verdict: PASS with notes**

The admin portal framing is coherent and well-motivated. The PRD does not
explicitly name a "university admin" persona (primary persona is the dyslexic
student), but PRD §10 success metrics require a "user-reported wrong word rate"
north-star signal — which demands a human reviewer loop. The admin persona is
a reasonable inference. Recorded as ASM-F33-01.

**Finding (Medium):** The portal is framed as a quality review tool but design.md
title still says "Side-by-Side Debug Viewer". This creates a communication mismatch:
developers see "debug" while admins see "review". Recommend aligning terminology
in user_stories.md (already uses "Exam Review Portal") and updating design.md title
in the next sw-designpipeline pass.

**Finding (Low):** US-01 AC-01 says "within 3 seconds" for PDF render. This is a
functional constraint, not a quality SLO — move to a test note rather than AC.

---

## Reviewer 2: DDD

**Verdict: PASS with notes**

`ReviewSession` is the correct aggregate root: it owns the lifecycle of a single
admin review for a specific run. `WordAnnotation` living inside `ReviewSession` is
correct — an annotation cannot exist without a session context.

**Finding (High):** The design has `ReviewSession` scoped to "per run, per admin
session" but there is no `SessionId` — only a `RunId`. In a multi-admin future,
two admins reviewing the same run would conflict. For single-user POC this is
acceptable. **Recommend:** add `SessionId` as a value object in the DDD model even
for POC, so the schema is forward-compatible. Document as deferred; do not block.

**Finding (Medium):** `IssueCategory` as a value object is correct. However the
design.md lists 4 categories but AC-06 in user_stories.md lists 5 (Wrong nikud /
Wrong stress / Wrong order / Wrong pronunciation / Other). Alignment needed.

---

## Reviewer 3: Functional Testing

**Verdict: PASS**

FT-316 through FT-330 cover the required 10+ cases. Coverage of boundary conditions
is good: empty annotation (FT-321), empty export (FT-328), 50+ artifacts (FT-329),
special chars in markId (FT-327).

**Finding (Low):** FT-326 tests word-sync highlight "continues working" but does not
specify what "correctly" means — needs a measurable assertion (e.g., ≤ 80 ms per
FT-244). Addressed in FT-326 update.

**Finding (Low):** No test for `stages_visible_at_capture` population. Addressed
in FT-320 note: array must contain only stages actually opened by the admin.

---

## Reviewer 4: Behavioural UX

**Verdict: PASS**

BT-209 through BT-218 cover 10 scenarios covering all required behavioural patterns
(hesitation, rework, partial info, abandoned flow, retry, endurance).

**Finding (Medium):** BT-211 (admin has no pipeline knowledge) is the highest-risk
UX scenario. The test relies on "plain language stage labels" but the test plan
does not define what "plain language" means — the label mapping should be enumerated
in implementation tasks (e.g., `06-diacritize` → "Diacritized text"). Deferred.

**Finding (Low):** BT-218 (QA reviewer) is useful as an end-to-end smoke scenario.
Mark as SMOKE.

---

## Reviewer 5: Architecture

**Verdict: PASS with questions**

The local `output/<N>/` abstraction is clean for POC. The design states that GCS
is the production path — but F33's JS code fetches from relative `output/<N>/`
URLs. For GCS production, the base URL would be a signed URL prefix.

**Finding (High):** No abstraction layer between `sidebar.js` and the storage
backend URL. For POC, `output/<N>/manifest.json` is a relative local path.
For production GCS, it would be a signed URL prefix. Without a `TIRVI_ARTIFACT_BASE_URL`
environment variable, the code will require edits to go to production.

**Finding (Low):** The `--debug` flag in `scripts/run_demo.py` is the gate for
enabling the debug sink. Correct per D-02. No finding.
