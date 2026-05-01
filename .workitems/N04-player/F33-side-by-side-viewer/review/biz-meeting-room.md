---
feature_id: N04/F33
review_type: meeting-room
participants: [Product Strategy, DDD, Behavioural UX, Architecture, Delivery Risk]
date: 2026-05-01
format: structured-transcript-summary
---

# Meeting Room Review — N04/F33 Exam Review Portal

## Focus Areas

1. Admin portal framing vs. debug tool identity
2. Deferred auth decision — is it truly safe?
3. Feedback schema forward-compatibility with F39

---

## Topic 1: Admin Portal Framing vs. Debug Tool

**Product Strategy** opened: The original design.md title is "Side-by-Side Debug
Viewer". The user_stories.md correctly reframes it as "Exam Review Portal". These
two names point at different audiences. A debug viewer is for developers.
An admin portal is for non-technical staff. Which is it?

**DDD** responded: Both. The bounded context `bc:exam_review` supports two
personas: University Admin (quality review, pre-term sign-off) and Pipeline
Developer (diagnosis during development). The three-panel layout serves both.
The key insight is that the admin use case is the PRIMARY driver — the developer
use case is a bonus that the same UI satisfies for free.

**Behavioural UX** agreed, with a caveat: the UI must be designed for the admin
first. If stage labels, artifact previews, and the feedback panel are optimized
for developers (raw file names, raw JSON dumps), the admin will be lost. The
design must commit to human-readable labels as a first-class constraint, not
a polish item.

**Delivery Risk** noted: this creates a tension. Human-readable labels require
a mapping table (code). That mapping table must be maintained as the pipeline
evolves. If we ship with raw directory names and label it "v0", teams will
accept it as permanent.

**Resolution:** User_stories.md (US-03 AC-13) is authoritative: "Stage labels are
human-readable — not raw file names like `06-diacritize/raw-response.json`."
This is a hard AC, not optional. The mapping table (`01-ocr` → "OCR words",
`06-diacritize` → "Diacritized text") must appear in the implementation tasks.
Design.md title to be updated by sw-designpipeline.

---

## Topic 2: Deferred Auth Decision

**Product Strategy** raised: the design says auth is deferred and the portal is
open. This is documented. But staging deployments are accessed over a network.
Is "documented deferral" sufficient, or do we need a technical gate?

**Architecture** responded: for a local `python -m http.server` POC, open is fine.
The risk materializes only when the portal is deployed to a network-accessible
staging URL. The deferred-fixes.md must state the re-evaluation trigger as
"before any deployment that exposes the portal on a network reachable by more
than one machine."

**Behavioural UX** added: BT-218 (QA reviewer) validates the "open portal" use case
for staging. This is the intended audience for the deferral: internal QA and
admins on a trusted network, not public internet.

**DDD** noted: single-user POC assumption (design.md D-04 equivalent) means no
concurrent review collision handling. This is fine for POC. The bounded context
model (`ReviewSession`) should anticipate future multi-user, but the ACCs do not
need to test it now.

**Resolution:** deferred-fixes.md to record: "Auth/security deferred for POC.
Re-evaluate before any network-accessible staging deployment. Minimum: HTTP basic
auth for staging environment. Full auth tracked as separate NFR."

---

## Topic 3: Feedback Schema Forward-Compatibility with F39

**Product Strategy** asked: F39 (tirvi-bench-v0) will consume the feedback JSON.
What happens if F33 ships feedback schema v1 and F39 has hard expectations about
field names?

**DDD** answered: the schema is defined in design.md. It is stable for POC:
`run, markId, word, stages_visible_at_capture, issue, severity, note, ts`.
The `stages_visible_at_capture` field is the forward-compatible hook — it records
which stages were visible when the admin submitted, which lets F39 correlate
feedback to pipeline version.

**Architecture** noted the missing `schema_version` field. Without it, F39 cannot
distinguish v1 from v2 feedback files when schema evolves. This is a 1-field
addition, zero cost.

**Delivery Risk** agreed this is a low-risk fix that should be done now, not later.
Adding `schema_version` after deployment means existing files have no version tag
and F39 must treat "no version = v1".

**Resolution:** Add `"schema_version": "1"` to the feedback JSON schema in design.md
before TDD. This is a critical fix. F39 will use `schema_version` to determine
parse strategy.

---

## Decisions Recorded

| Decision | Owner | Priority |
|----------|-------|----------|
| Human-readable stage labels are a hard AC, not polish | user_stories.md AC-13 | High |
| Auth deferral trigger: "before any network deployment" | deferred-fixes.md | High |
| `schema_version: "1"` added to feedback JSON schema | design.md + FT-327 | High |
| `TIRVI_ARTIFACT_BASE_URL` config point for GCS migration | design.md interfaces | Medium |
| SessionId VO: document in DDD model, defer implementation | DDD model TODO | Low |
