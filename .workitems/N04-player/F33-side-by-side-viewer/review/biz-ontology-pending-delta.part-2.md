---
feature_id: N04/F33
type: pending-ontology-delta
target_files: [ontology/testing.yaml]
blocked_by: settings.json deny rules for current branch
part: 2-of-2
continued_from: biz-ontology-pending-delta.md
date: 2026-05-01
---

# Pending Ontology Delta — N04/F33 (Part 2 of 2)

Delta for `ontology/testing.yaml`. Part 1 contains `ontology/business-domains.yaml` delta.

---

## Delta 2: ontology/testing.yaml

### Add to `test_ranges` array:

```yaml
  - { feature_id: N04/F33, ft: [FT-316, FT-330], bt: [BT-209, BT-218] }
```

### Add to `functional_tests` array:

```yaml
  - id: FT-316
    name: Portal loads valid run — PDF page + audio player rendered
    feature_id: N04/F33
    epic_id: E10-F33
    test_file: .workitems/N04-player/F33-side-by-side-viewer/functional-test-plan.md
    test_type: functional
    related_stories: [US-01]
    related_business_objects: [BO49, BO52]
    related_contexts: [BC13]
    related_aggregates: [BO49]
    priority: critical
    risk_covered: Admin cannot start review without portal loading (R-F33-04)
    status: drafted

  - id: FT-320
    name: Word annotation persisted to localStorage and feedback JSON
    feature_id: N04/F33
    epic_id: E10-F33
    test_file: .workitems/N04-player/F33-side-by-side-viewer/functional-test-plan.md
    test_type: functional
    related_stories: [US-02]
    related_business_objects: [BO49, BO50, BO51, BO53]
    related_contexts: [BC13]
    related_aggregates: [BO49]
    priority: critical
    risk_covered: Feedback capture is the primary quality loop (PRD §10)
    status: drafted

  - id: FT-322
    name: Feedback export produces valid JSON matching schema
    feature_id: N04/F33
    epic_id: E10-F33
    test_file: .workitems/N04-player/F33-side-by-side-viewer/functional-test-plan.md
    test_type: functional
    related_stories: [US-04]
    related_business_objects: [BO49, BO50, BO51, BO52, BO53]
    related_contexts: [BC13]
    priority: critical
    risk_covered: F39 downstream consumes this schema; forward-compat required
    status: drafted

  - id: FT-327
    name: Feedback JSON schema — schema_version, XSS boundary, markId safety
    feature_id: N04/F33
    epic_id: E10-F33
    test_file: .workitems/N04-player/F33-side-by-side-viewer/functional-test-plan.part-2.md
    test_type: functional
    related_stories: [US-04]
    related_business_objects: [BO50, BO51, BO52, BO53]
    related_contexts: [BC13]
    priority: critical
    risk_covered: XSS via note field; path traversal via markId; schema_version forward-compat
    status: drafted
```

### Add to `behavioural_tests` array:

```yaml
  - id: BT-209
    name: Admin pauses mid-annotation, navigates away — draft restored on reload
    feature_id: N04/F33
    epic_id: E10-F33
    test_file: .workitems/N04-player/F33-side-by-side-viewer/behavioural-test-plan.md
    test_type: behavioural
    related_personas: [P08]
    related_stories: [US-02]
    behaviour_pattern: abandoned_flow
    priority: high
    risk_covered: Lost annotations degrade admin trust
    status: drafted

  - { id: BT-211, name: "Admin with no pipeline knowledge identifies diacritization stage", feature_id: N04/F33, epic_id: E10-F33, test_file: ".workitems/N04-player/F33-side-by-side-viewer/behavioural-test-plan.md", test_type: behavioural, related_personas: [P08], related_stories: [US-03], behaviour_pattern: partial_info, priority: high, risk_covered: "R-F33-04 — admin has zero pipeline knowledge", status: drafted }

  - { id: BT-215, name: "Admin reviews 200 words in single session — UI remains fluid", feature_id: N04/F33, epic_id: E10-F33, test_file: ".workitems/N04-player/F33-side-by-side-viewer/behavioural-test-plan.md", test_type: behavioural, related_personas: [P08], related_stories: [US-07], behaviour_pattern: endurance, priority: high, risk_covered: "Long session usability; localStorage quota; export at 200 entries", status: drafted }
```
