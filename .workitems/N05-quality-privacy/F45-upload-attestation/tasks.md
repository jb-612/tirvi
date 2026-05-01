---
feature_id: N05/F45
status: ready
total_estimate_hours: 2
deferred: true
---

# Tasks: F45 — Upload Attestation (No-PII Verification Gate)

Stub task list. Feature is deferred post-POC. Tasks will be expanded when
biz-functional-design runs for N05.

## T-01: Extend upload API with attestation field and write attestation record

- [x] **T-01 done**

- design_element: DE-01, DE-02
- acceptance_criteria: [AC-01]
- estimate: 2h
- test_file: tests/unit/test_upload_attestation.py
- dependencies: []
- hints: Add attested_no_pii: bool to POST /documents request schema; reject with
  HTTP 422 if false/absent; write manifests/{doc_id}/attestation.json to GCS on success.

## Dependency DAG

```
T-01
```
