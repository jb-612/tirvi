---
feature_id: N04/F33
plan_type: behavioural
bt_range: [BT-209, BT-218]
part: 1-of-2
continued_in: behavioural-test-plan.part-2.md
stories_ref: user_stories.md
personas: [University Admin, Pipeline Developer, QA Reviewer]
---

# Behavioural Test Plan — N04/F33 Exam Review Portal (Part 1 of 2)

BT-209..BT-214 here. BT-215..BT-218 in `behavioural-test-plan.part-2.md`.

## BT-209: Admin pauses mid-annotation and navigates away — draft not lost

**Story:** US-02 (behavioural note: abandoned flow)
**Behaviour pattern:** abandoned_flow
**Persona:** University Admin
**Scenario:**
  Admin opens a word annotation panel and types a note but does not submit.
  The browser tab is closed and reopened to the same run URL.
**Expected:** the annotation draft (note text, selected issue category) is
  restored from localStorage. The admin can continue and submit without
  re-entering the note.
**Risk covered:** Data loss on accidental close degrades admin trust in the tool.

---

## BT-210: Admin re-annotates the same word twice — latest annotation wins

**Story:** US-02 (behavioural note: rework)
**Behaviour pattern:** rework
**Persona:** University Admin
**Scenario:**
  Admin annotates word `ספר` with "Wrong nikud". Later in the session they
  realize the issue is actually "Wrong stress". They click the word again
  and submit with "Wrong stress".
**Expected:** only the latest annotation is stored; the feedback file
  reflects "Wrong stress", not "Wrong nikud". The visual marker on the
  word reflects the updated state. The review list shows one entry, not two.
**Risk covered:** Stale annotations pollute feedback signal to F39.

---

## BT-211: Admin has no pipeline knowledge — artifact tree is self-explanatory

**Story:** US-03 (behavioural note: partial info)
**Behaviour pattern:** partial_info
**Persona:** University Admin (non-technical)
**Scenario:**
  Admin hears incorrect pronunciation and opens the artifact tree with zero
  knowledge of OCR, NLP, or SSML. They read the stage labels and can
  identify "Diacritized text" as the likely problem area without developer
  assistance.
**Expected:** stage labels use plain language; hovering or expanding a stage
  shows a one-line description; the admin can identify the diacritization stage
  without knowing what "Nakdan" or "06-diacritize" means.
**Risk covered:** R-F33-04 — admin has zero pipeline knowledge.

---

## BT-212: Admin submits feedback then realizes error — can delete and re-annotate

**Story:** US-07 / AC-31 (behavioural note: correction)
**Behaviour pattern:** error_correction
**Persona:** University Admin
**Scenario:**
  Admin submits annotation for word `מה` with issue "Wrong order" and note
  "reads backwards". They then notice they flagged the wrong word. They open
  the review list, locate the entry, and delete it. They navigate the player
  to the correct word and annotate it correctly.
**Expected:** deletion removes the feedback file for that markId; the review
  list updates immediately; the re-annotation creates a new file.

---

## BT-213: Developer drills from bad audio → artifact tree → stage → root cause

**Story:** US-05 (behavioural note: deep drill)
**Behaviour pattern:** deep_drill
**Persona:** Pipeline Developer
**Scenario:**
  Developer hears word `ד"ר` read as `דר` (missing expansion). They open the
  artifact tree, click "Normalized text" (04-normalize), see the expansion
  is missing, then click "NLP tokens" and "Diacritized text" to confirm the
  error originated at normalization. They confirm by opening the artifact directly.
**Expected:** developer can traverse all stages in one session without losing
  context; artifact content is raw pipeline output (not transformed for display).

---

## BT-214: Admin exports feedback, developer parses JSON without documentation

**Story:** US-04 (behavioural note: hand-off)
**Behaviour pattern:** cross_persona_hand_off
**Personas:** University Admin (sender), Pipeline Developer (receiver)
**Scenario:**
  Admin exports `feedback-run-001-<ts>.json`. Developer receives the file and
  opens it in a JSON viewer. They can understand field names without reading
  design.md: `markId`, `word`, `issue`, `note`, `ts` are self-explanatory.
**Expected:** field naming is self-documenting; `issue` enum values use
  plain English ("wrong_nikud", "wrong_stress"); no opaque IDs require lookup.
**Risk covered:** BT-214 tests feedback schema legibility end-to-end.
