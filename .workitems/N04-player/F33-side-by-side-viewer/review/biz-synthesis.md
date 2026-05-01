---
feature_id: N04/F33
review_type: synthesis
date: 2026-05-01
---

# Business Design Synthesis — N04/F33 Exam Review Portal

## Feature Summary

F33 is reframed from a developer-centric "Side-by-Side Debug Viewer" to an
**Admin Review Portal** that serves university admins as the primary persona.
The portal provides three panels: PDF + audio player (center), artifact tree
(left), feedback capture (right). It folds in N05/F47 feedback capture as a
single coherent quality loop.

## Persona Alignment

| Persona | Role | Primary Stories |
|---------|------|----------------|
| University Admin | Quality sign-off before term; non-technical | US-01..US-04, US-06, US-07 |
| Pipeline Developer | Root cause diagnosis during development | US-05 |
| QA / Staging Reviewer | Validates before production promotion | US-01, US-04 (BT-218) |
| Content Preparer | Non-technical exam assembly | US-01, US-02 (secondary) |

## Bounded Context

`bc:exam_review` — new, subordinate to `player` (BC10) and `quality_assurance` (BC12).

## DDD Model (Summary)

- **Aggregate root:** `ReviewSession` (per run + per admin session; SessionId deferred)
- **Entities:** `WordAnnotation` (owned by ReviewSession)
- **Value objects:** `IssueCategory`, `RunId`, `MarkId`
- **Domain events:** `AnnotationSubmitted`, `FeedbackExported`, `ArtifactInspected`
- **Commands:** `LoadRun`, `AnnotateWord`, `ExportFeedback`, `BrowseArtifact`
- **Policies:** `FeedbackMustHaveCategory`, `AnnotationPersistsAcrossPageReloads`
- **External systems:** Pipeline artifact store (local `output/<N>/`; GCS in production), F48 FeedbackAggregator

## Test Coverage Summary

- 15 functional tests (FT-316..FT-330) covering all 7 user stories
- 10 behavioural tests (BT-209..BT-218) covering all required patterns
- FT-327 covers schema validation, XSS boundary, and path traversal boundary
- BT-211 covers non-technical admin (highest UX risk)
- BT-215 covers endurance (200-word session)

## Key Constraints Confirmed

1. Security/auth: intentionally deferred; open portal is localhost-only for POC.
   Re-evaluation trigger: before any network-accessible deployment.
2. Single-user POC: no concurrent review collision handling.
3. Local filesystem for POC; `TIRVI_ARTIFACT_BASE_URL` environment variable
   enables GCS migration without code changes.
4. Feedback schema v1: `{run, markId, word, stages_visible_at_capture, issue,
   severity, note, ts, schema_version}` — frozen for F39 compatibility.
5. Issue categories: 5 values (`wrong_nikud | wrong_stress | wrong_order |
   wrong_pronunciation | other`).

## Dependency Summary

| Dependency | Direction | Strength |
|-----------|-----------|---------|
| N04/F35 word-sync marker | F33 requires | Strong |
| N03/F30 audio.json | F33 requires | Strong |
| N02/F22 reading-plan-output | F33 requires | Strong |
| N04/F50 inspector tabs | F50 uses F33 as host | Medium |
| N02/F48 FeedbackAggregator | F33 produces feedback for F48 | Strong |
| N05/F39 tirvi-bench-v0 | F33 feeds quality signal | Medium |

## Known Deferrals

See `deferred-fixes.md` for full list. Key items:
- Auth/security (intentional, pre-approved)
- SessionId VO for multi-admin forward compatibility
- Stage label enumeration mapping (sw-designpipeline tasks)
- FT-326 highlight timing bound (link to FT-244)

## Handoff to sw-designpipeline

The following biz artifacts are ready for sw-designpipeline consumption:
- `user_stories.md` — 7 stories with Gherkin ACs
- `functional-test-plan.md` — 15 FTs
- `behavioural-test-plan.md` — 10 BTs
- `biz-severity-ranked-fixes.md` — ordered list for implementation reference

sw-designpipeline should:
1. Update design.md title to "Exam Review Portal"
2. Align issue category count to 5 in design.md
3. Add `schema_version: "1"` to design.md feedback JSON schema
4. Add `TIRVI_ARTIFACT_BASE_URL` to design.md interfaces table
5. Add XSS and path traversal mitigations to design.md Risks table
