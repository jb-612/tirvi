---
feature_id: N05/F40
feature_type: integration
status: designed
hld_refs: ["HLD-§5.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — CI quality gates excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F40 — CI Quality Gate Runner (pytest-based bench gates)

## Overview

Integrates the F39 benchmark harness results into CI as enforceable quality
gates using pytest. A failing gate blocks merges when word-error-rate or
MOS-proxy regresses beyond configured thresholds. Deferred to post-POC.

## biz_corpus

corpus_e_id: E10-F02
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [F39 benchmark harness]
- Adapter ports consumed: [OCRBackend, TTSBackend]
- External services: [Cloud Storage (HLD-§3.4), CI runner (GitHub Actions)]

## Design Elements

- DE-01: pytest plugin / conftest that reads the latest benchmark results JSON
  from GCS and asserts metrics are within threshold (ref: HLD-§5.4/FeedbackLoop)
- DE-02: Threshold configuration file (`bench/thresholds.yaml`) versioned in
  repo; CI step invokes `pytest tests/bench/` (ref: HLD-§5.4)

## Approach

1. DE-01: conftest.py fixture fetches `bench/latest/results.json`, exposes
   per-page metrics as pytest parameters.
2. DE-02: `thresholds.yaml` defines `max_wer` and `min_mos_proxy`; test
   assertions fail CI if any page exceeds limits.

## Decisions

- pytest chosen for consistency with existing Python test suite.
- Thresholds versioned in repo so regressions are traceable to commits.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- HLD §12: threshold values TBD — will be baselined from first F39 run.

## Risks

1. Flaky gates from GCS latency — mitigated by caching results artifact in CI.
2. Threshold calibration effort — mitigated by starting permissive, tightening over sprints.
3. Gate added overhead to CI — mitigated by running bench tests in a separate optional job.

## Out of Scope

- MOS human panel (F41), cost profiling (F42), benchmark runner itself (F39).
