---
feature_id: N04/F33
review_type: biz-design
round: R1
reviewers: 10 (parallel)
part: 2-of-2
continued_from: biz-design-review.md
date: 2026-05-01
---

# Business Design Review — N04/F33 Exam Review Portal (Part 2 of 2)

Reviewers 6–10 and Team Lead Synthesis. Reviewers 1–5 in part 1.

## Reviewer 6: Data / Ontology

**Verdict: PASS with notes**

The `output/<N>/feedback/<markId>-<ts>.json` schema in design.md is explicit and
covers all required fields. The `stages_visible_at_capture` field provides forward
traceability to F39.

**Finding (Medium):** The feedback schema does not include a `schema_version` field.
When F39 consumes feedback files from older runs, it has no way to detect format
changes. Recommend adding `"schema_version": "1"` to the schema. This costs one
field now and avoids a breaking change later.

**Finding (Low):** The `issue` enum has 5 values in user_stories.md but design.md
lists 4 buttons. Align enum definition across both files before TDD.

---

## Reviewer 7: Security / Compliance

**Verdict: CONDITIONAL PASS — deferral documented**

The intentional auth deferral is acknowledged. The portal is "open for all" by
design in POC/staging. This is an accepted risk documented in writing.

**Finding (High — intentional deferral):** XSS via the free-text note field if
annotations are re-rendered in the review list using `innerHTML`. Use `textContent`.
This is a 1-line fix; mark as Critical-but-simple.

**Finding (Medium):** Auth deferral must be tracked in deferred-fixes.md
with a re-evaluation trigger ("before any network-accessible deployment").

---

## Reviewer 8: Delivery Risk

**Verdict: PASS**

Smallest deployable increment: (1) static HTML three-panel grid, (2) artifact tree
from a hand-crafted `manifest.json`, (3) feedback panel writing to a local file.
Can be done without the full pipeline running.

**Finding (Low):** US-06 (run comparison) depends on two actual pipeline runs.
Mark US-06 as "demo-mode blocked" until end-to-end pipeline produces `output/002/`.

**Finding (Low):** DebugSink is coupled to pipeline stage sequence. Stage name
changes require sink + manifest updates in sync. Maintenance risk, not delivery.

---

## Reviewer 9: Adversarial

**Verdict: PASS with security note**

**Finding (High):** Free-text note field XSS. Same as Reviewer 7. The note is
stored as raw text in JSON, then re-rendered in the review list. Use `textContent`.

**Finding (Medium):** The `markId` field in the feedback filename is user-influenced
(from audio timing marks). A markId containing `..` or `/` could cause path
traversal. Validate markId against `[a-zA-Z0-9-]+` at the feedback endpoint.

**Finding (Low):** Export filename colons on Windows (`2026-05-01T18:55:00Z`).
Use `2026-05-01T185500Z` format for the filename component.

---

## Reviewer 10: Team Lead Synthesis

**Verdict: CONDITIONAL PASS**

| Severity | Count | Key Issues |
|----------|-------|-----------|
| High | 4 | SessionId VO; storage URL abstraction; XSS; markId path traversal |
| Medium | 4 | Category count mismatch; schema_version missing; label mapping; auth deferral |
| Low | 6 | Various; non-blocking |

**Required before TDD starts:**
1. Align issue category count to 5 across design.md and user_stories.md.
2. Add `schema_version: "1"` to feedback JSON schema in design.md.
3. Add `TIRVI_ARTIFACT_BASE_URL` config point to design.md interfaces section.
4. Document XSS mitigation (`textContent`) in design.md Risks.
5. Add markId validation note to feedback server endpoint spec.
6. Auth deferral in deferred-fixes.md with re-evaluation trigger.

**Accepted deferral:** SessionId VO — document in DDD model as TODO; do not block.
**Accepted deferral:** stage label mapping — define in implementation tasks.
**Stage gate:** iteration log must confirm all High issues addressed before TDD.
