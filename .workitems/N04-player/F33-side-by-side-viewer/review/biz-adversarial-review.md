---
feature_id: N04/F33
review_type: adversarial
part: 1-of-2
continued_in: biz-adversarial-review.part-2.md
date: 2026-05-01
---

# Adversarial Review — N04/F33 Exam Review Portal (Part 1 of 2)

Challenges 1–3 here. Challenges 4–5 and Summary in part 2.

## Challenge 1: Is the "admin" persona real or assumed?

**Challenge:** The PRD §3 Target Users lists "Hebrew-speaking students" as primary
and "accommodation coordinators and learning-support teachers" as secondary. Neither
maps cleanly to "university admin" or "university accommodation coordinator". Where
does this persona come from?

**Evidence review:**
- PRD §6.4 mentions "user feedback: this word was read wrong — captured for offline
  improvement". This implies a human reviewer but does not name them.
- PRD §10 success metrics include "user-reported wrong word rate tracked as a
  north-star quality signal". Again, implies a reviewer loop.
- design.md explicitly introduces the persona in its overview.
- The task brief for F33 explicitly reframes it as an "Admin Review Portal".

**Finding:** The admin persona is an inference from the feedback-loop requirement,
not a named PRD persona. This is legitimate product reasoning (someone must close
the feedback loop), but it should be captured as a product assumption.

**Verdict:** Acceptable inference. Recorded as ASM-F33-01 in source-inventory.md.
If a product manager disputes this persona, F33's entire motivation changes. The
risk is low given that the task brief explicitly approves the reframing.

---

## Challenge 2: What if two admins review simultaneously?

**Challenge:** The design says "single-user POC; no concurrent review collision
handling needed yet." But if two members of the accommodation office review the
same run, their localStorage and feedback files will be independent. What happens
when they both export and send conflicting feedback?

**Evidence review:**
- design.md D-04: "Collisions impossible in single-user POC."
- The feedback files use `<markId>-<iso8601>.json` — two concurrent submits produce
  two files, not one. F48 FeedbackAggregator would see two entries for same markId.

**Finding:** The "single-user POC" assumption is not enforced by the system — it
is a documentation assumption. F48's aggregator must be designed to handle duplicate
markId entries (deduplicate by latest ts, or flag conflicts).

**Verdict:** Acceptable for POC. Document in deferred-fixes.md: "F48
FeedbackAggregator must deduplicate by markId+run using latest timestamp."

---

## Challenge 3: Is the feedback JSON schema stable enough for F39?

**Challenge:** F39 (tirvi-bench-v0) will consume feedback files produced by F33.
If F33's schema changes between now and when F39 is built, existing feedback files
become unreadable.

**Evidence review:**
- Current schema (design.md): `run, markId, word, stages_visible_at_capture,
  issue, severity, note, ts`. Eight fields. No `schema_version`.
- `stages_visible_at_capture` is fragile — an array of directory names that could
  change shape (e.g., from `["06-diacritize"]` to `[{stage, artifact}]`).

**Finding:** Schema is not versioned. Any field rename breaks F39.

**Verdict:** Critical but simple fix. Add `"schema_version": "1"`. Freeze
`stages_visible_at_capture` as an array of stage directory names for v1.
Document that v2 would be `stages_inspected: [{stage, artifact}]`.
