---
feature_id: N04/F33
plan_type: behavioural
bt_range: [BT-215, BT-218]
part: 2-of-2
continued_from: behavioural-test-plan.md
---

# Behavioural Test Plan — N04/F33 Exam Review Portal (Part 2 of 2)

BT-215..BT-218 here. BT-209..BT-214 in `behavioural-test-plan.md`.

## BT-215: Admin reviews 200 words in a single session — UI does not degrade

**Story:** US-07 (behavioural note: long session)
**Behaviour pattern:** endurance
**Persona:** University Admin
**Scenario:**
  Admin reviews a 12-page exam run with 200+ words annotated over 90 minutes.
  The review list grows to 200 entries. The admin can scroll, delete, and
  export without perceptible UI lag.
**Expected:** scrolling the review list remains fluid; export completes within
  2 seconds for 200 entries; localStorage does not exceed browser quota for
  200 feedback entries (each entry ~500 bytes → ~100 KB total).

---

## BT-216: Pipeline re-run after fix — admin loads new run and verifies improvement

**Story:** US-06 (behavioural note: retry after fix)
**Behaviour pattern:** retry
**Persona:** University Admin with Pipeline Developer
**Scenario:**
  Admin annotates three words in run 001 and exports. Developer applies fix
  and produces run 002. Admin uses run selector to switch to run 002, listens
  to the same words, and confirms the pronunciation is correct.
**Expected:** run 002's artifact tree and audio load without contamination from
  run 001's annotations; the run selector clearly identifies the new run.

---

## BT-217: Admin encounters a stage with empty/stub output — no crash, clear label

**Story:** US-05 / AC-22 (behavioural note: partial pipeline run)
**Behaviour pattern:** graceful_degradation
**Persona:** Pipeline Developer
**Scenario:**
  A partial pipeline run produces `05-nlp/tokens.json` with `{}` (stub NLP).
  Developer opens the artifact tree. The NLP stage is listed but clicking it
  shows the empty stub content without error.
**Expected:** empty artifact renders as `{}` in the JSON viewer; no crash; the
  manifest still lists the stage; stage label includes "(stub)" or "(empty)" indicator.

---

## BT-218: QA reviewer validates run before production promotion

**Story:** US-01, US-04 (QA persona)
**Behaviour pattern:** approval_workflow (SMOKE)
**Persona:** QA / Staging Reviewer
**Scenario:**
  QA reviewer receives a shared URL to run 003 on the staging portal. They
  listen to the entire exam, annotate two words, export the feedback, and
  share the JSON with the developer with a thumbs-up for the rest. No login
  required.
**Expected:** the portal loads without auth; QA can complete end-to-end review
  and export without needing a developer account; the deferred auth decision
  is documented (see deferred-fixes.md).
**Risk covered:** R-F33-01 intentional auth deferral; validates the "open by
  default" posture works for staging use cases without introducing risk to
  production.
