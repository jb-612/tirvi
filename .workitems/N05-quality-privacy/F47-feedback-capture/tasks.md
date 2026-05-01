---
feature_id: N05/F47
status: ready
total_estimate_hours: 2
deferred: true
---

# Tasks: F47 — User Feedback Capture for Lexicon/Quality Improvements

Stub task list. Feature is deferred post-POC. Tasks will be expanded when
biz-functional-design runs for N05.

## T-01: Implement feedback API endpoint and GCS record writer

- [x] **T-01 done**

- design_element: DE-01, DE-02
- acceptance_criteria: [AC-01]
- estimate: 2h
- test_file: tests/unit/test_feedback_capture.py
- dependencies: []
- hints: POST /documents/{id}/feedback validates word/page/expected_pronunciation;
  writes feedback/{doc_id}/{ts}.json to GCS via StoragePort; feedback/ prefix
  excluded from 7-day TTL lifecycle rule (F43).

## Dependency DAG

```
T-01
```
