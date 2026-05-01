---
feature_id: N04/F33
type: pending-ontology-delta
target_files: [ontology/business-domains.yaml, ontology/testing.yaml]
blocked_by: settings.json deny rules for current branch
part: 1-of-2
continued_in: biz-ontology-pending-delta.part-2.md
date: 2026-05-01
---

# Pending Ontology Delta — N04/F33 (Part 1 of 2)

These changes could not be applied directly because `ontology/business-domains.yaml`
and `ontology/testing.yaml` are write-denied in `settings.json` for this branch.
Apply this delta in a privileged session or when permissions are updated.

`ontology/dependencies.yaml` was successfully updated (DEP-110..DEP-115).

Part 2 (`biz-ontology-pending-delta.part-2.md`) contains the `ontology/testing.yaml` delta.

---

## Delta 1: ontology/business-domains.yaml

### Add to `domains[0].subdomains` array:

```yaml
      - id: D01-SD07
        name: Exam Quality Assurance
        type: supporting
        bounded_contexts:
          - id: BC13
            name: exam_review
            note: "N04/F33 — Admin Review Portal; subordinate to player (BC10) and quality_assurance (BC12)"
```

### Add to `business_objects` array:

```yaml
  # --- Exam Review (N04/F33) ---
  - id: BO49
    name: ReviewSession
    type: aggregate_root
    description: per-run admin review session; owns WordAnnotation entities; SessionId deferred for POC
    owned_by_context: exam_review
    related_features: [N04/F33]
  - id: BO50
    name: WordAnnotation
    type: entity
    description: per-word quality annotation with IssueCategory, severity, free-text note, timestamp
    owned_by_context: exam_review
    related_features: [N04/F33]
  - id: BO51
    name: IssueCategory
    type: value_object
    description: "enum: wrong_nikud | wrong_stress | wrong_order | wrong_pronunciation | other"
    owned_by_context: exam_review
    related_features: [N04/F33]
  - id: BO52
    name: RunId
    type: value_object
    description: monotonic three-digit run identifier (e.g. "001"); filesystem-safe; single-user POC
    owned_by_context: exam_review
    related_features: [N04/F33]
  - id: BO53
    name: MarkId
    type: value_object
    description: per-word audio timing mark identifier (e.g. "b1-3"); alphanumeric + hyphen only
    owned_by_context: exam_review
    related_features: [N04/F33]
  - id: BO54
    name: AnnotationSubmitted
    type: domain_event
    description: emitted when admin submits a word annotation; payload includes MarkId + IssueCategory
    owned_by_context: exam_review
    related_features: [N04/F33]
  - id: BO55
    name: FeedbackExported
    type: domain_event
    description: emitted when admin downloads feedback JSON for a run
    owned_by_context: exam_review
    related_features: [N04/F33]
  - id: BO56
    name: ArtifactInspected
    type: domain_event
    description: emitted when admin or developer opens a stage artifact in the preview panel
    owned_by_context: exam_review
    related_features: [N04/F33]
```

### Add to `plan_md_cross_walk` array:

```yaml
  - skill_epic: E10-F33
    plan_phase: N04-player
    skill_features: [E10-F33]
    plan_features: [F33-side-by-side-viewer]
    notes: F33 folds in N05/F47 feedback-capture. Admin Review Portal cross-walk.
```

### Add to `epics` array:

```yaml
  - id: E10-F33
    name: Exam Review Portal
    description: admin review portal — three-panel layout, artifact tree, per-word annotation, feedback export; folds N05/F47 feedback-capture
    bounded_context: exam_review
```

### Add to `personas` array (P08–P10 are new; P01–P07 already exist):

```yaml
  - { id: P08, name: University Admin / Accommodation Coordinator, role: "primary F33; quality review pre-term; non-technical", collaboration_level: solo }
  - { id: P09, name: Pipeline Developer, role: "supporting F33; artifact tree diagnosis during dev", collaboration_level: solo }
  - { id: P10, name: QA / Staging Reviewer, role: "supporting F33; validates before production promotion", collaboration_level: solo }
```
