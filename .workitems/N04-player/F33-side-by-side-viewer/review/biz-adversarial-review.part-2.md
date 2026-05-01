---
feature_id: N04/F33
review_type: adversarial
part: 2-of-2
continued_from: biz-adversarial-review.md
date: 2026-05-01
---

# Adversarial Review — N04/F33 Exam Review Portal (Part 2 of 2)

Challenges 4–5 and Summary. Challenges 1–3 in part 1.

## Challenge 4: Is "open for all" truly safe even during staging?

**Challenge:** The design says auth is deferred and the portal is "open." In
staging environments, the portal serves:
- Pipeline artifacts (intermediate OCR/NLP/TTS output) which may contain exam content
- Feedback files which may contain admin annotations with free-text notes

**Evidence review:**
- PRD §8: "Exams may be confidential. Default retention: 7 days TTL."
- PRD §8: "Uploads are scoped to the uploading session/user; no cross-user access."
- The portal serves files from `output/<N>/` via `python -m http.server` which
  serves the entire `output/` directory to any client that can reach the port.

**Finding:** The open portal is safe only for localhost. If the demo server is
started on a VM or shared machine and port 8080 is exposed, any network user can:
1. Browse all pipeline runs and their intermediate artifacts.
2. Read all admin feedback annotations.
3. Inject XSS via note field (see biz-design-review.part-2.md Reviewer 9).

**Verdict:** Acceptable risk for localhost POC. Not acceptable for any VM-based
staging. The deferred-fixes.md must be explicit: "Staging deployment requires
HTTP basic auth at minimum. Open portal is localhost-only for POC."

---

## Challenge 5: XSS in free-text note field

**Challenge:** The feedback note is stored as a string in JSON. When the review
list renders annotations, if `innerHTML` is used to display the note, a payload
with `<script>` tags would execute.

**Evidence review:**
- Standard DOM API: `element.innerHTML = note` executes embedded scripts.
  `element.textContent = note` does not.
- The review list (US-07 / AC-29) displays the note inline.
- No sanitization is mentioned in the design.

**Finding:** This is a real XSS vector for any multi-user staging scenario.
It is a 1-character fix: use `textContent` everywhere notes are rendered.

**Verdict:** Critical-but-simple. Applied to FT-327 boundary condition.
Add to design.md Risks table: "Note field XSS: use textContent, not innerHTML."

---

## Summary

| Challenge | Verdict | Disposition |
|-----------|---------|------------|
| Admin persona evidence | Acceptable inference | ASM-F33-01 |
| Concurrent review collision | Acceptable for POC | deferred-fixes.md note |
| Feedback schema stability | Critical fix: add schema_version | Applied before TDD |
| Open portal staging safety | Acceptable localhost-only | deferred-fixes.md trigger |
| XSS in note field | Critical fix: use textContent | Applied before TDD |

No findings block the story set. Two critical fixes (schema_version, textContent)
were applied to user_stories.md AC-18 and FT-327 before TDD starts.
