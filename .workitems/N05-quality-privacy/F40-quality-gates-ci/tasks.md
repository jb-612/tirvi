---
feature_id: N05/F40
status: ready
total_estimate_hours: 2
deferred: true
---

# Tasks: F40 — CI Quality Gate Runner (pytest-based bench gates)

Stub task list. Feature is deferred post-POC. Tasks will be expanded when
biz-functional-design runs for N05.

## T-01: Implement pytest bench gates and threshold configuration

- [x] **T-01 done**

- design_element: DE-01, DE-02
- acceptance_criteria: [AC-01]
- estimate: 2h
- test_file: tests/unit/test_quality_gates.py
- dependencies: [F39/T-01]
- hints: conftest.py fixture fetches bench/latest/results.json from GCS;
  thresholds.yaml configures max_wer and min_mos_proxy; CI runs pytest tests/bench/.

## Dependency DAG

```
T-01
```
