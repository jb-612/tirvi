---
feature_id: N05/F43
status: ready
total_estimate_hours: 2
deferred: true
---

# Tasks: F43 — Draft TTL Automation (Expiry + Cleanup)

Stub task list. Feature is deferred post-POC. Tasks will be expanded when
biz-functional-design runs for N05.

## T-01: Configure GCS lifecycle rules and implement cleanup verification script

- [x] **T-01 done**

- design_element: DE-01, DE-02
- acceptance_criteria: [AC-01]
- estimate: 2h
- test_file: tests/unit/test_ttl_automation.py
- dependencies: []
- hints: Apply GCS lifecycle_rule for pdfs/, pages/, plans/, manifests/ prefixes
  with 7-day Age condition; exclude audio/; scripts/ops/verify_ttl.py checks rule is active.

## Dependency DAG

```
T-01
```
