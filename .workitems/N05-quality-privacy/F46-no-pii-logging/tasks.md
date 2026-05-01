---
feature_id: N05/F46
status: ready
total_estimate_hours: 2
deferred: true
---

# Tasks: F46 — No-PII Logging Guard (Structured Log Scrubber)

Stub task list. Feature is deferred post-POC. Tasks will be expanded when
biz-functional-design runs for N05.

## T-01: Implement PiiScrubFilter middleware and scrub_config.yaml

- [ ] **T-01 done**

- design_element: DE-01, DE-02
- acceptance_criteria: [AC-01]
- estimate: 2h
- test_file: tests/unit/test_pii_scrub_filter.py
- dependencies: []
- hints: PiiScrubFilter(logging.Filter) walks log record extra dict; replaces
  sensitive key values with [REDACTED]; config at logging/scrub_config.yaml loaded at startup.

## Dependency DAG

```
T-01
```
