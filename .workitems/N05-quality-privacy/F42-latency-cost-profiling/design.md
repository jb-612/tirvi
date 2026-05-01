---
feature_id: N05/F42
feature_type: integration
status: designed
hld_refs: ["HLD-§5.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — latency/cost profiling excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F42 — Latency and Cost Profiling per Page

## Overview

Instruments the OCR → NLP → TTS pipeline to record per-page wall-clock
latency and Cloud API cost (tokens billed, TTS characters, Cloud Vision
pages). Results are stored alongside benchmark metrics for budgeting and
SLA analysis. Deferred to post-POC.

## biz_corpus

corpus_e_id: E10-F04
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [F39 benchmark harness]
- Adapter ports consumed: [OCRBackend, TTSBackend]
- External services: [Cloud Storage (HLD-§3.4), Cloud Billing API]

## Design Elements

- DE-01: Timing decorator / context manager wrapping each pipeline stage;
  captures wall-clock latency per stage and per page (ref: HLD-§5.4)
- DE-02: Cost estimator module that maps API call counts to billing units
  using a configurable unit-price table; writes `bench/{run_id}/cost.json`
  (ref: HLD-§5.4/FeedbackLoop)

## Approach

1. DE-01: Wrap OCRBackend.process(), NLP.analyse(), TTSBackend.synthesise()
   with a timer context manager; aggregate into a per-page latency record.
2. DE-02: Post-process call logs to estimate cost in USD; store alongside
   latency in GCS.

## Decisions

- Instrumentation is passive (no sampling agent); adds < 5 ms overhead.
- Unit-price table is a static YAML file; update manually when pricing changes.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- HLD §12: cloud billing API integration vs. static price table — deferred.

## Risks

1. Price table staleness — mitigated by version-controlled YAML with last-updated date.
2. Latency measurement noise in shared CI environment — mitigated by noting environment in report.
3. Cost estimate inaccuracy for cached OCR results — mitigated by flagging cache hits.

## Out of Scope

- Real-time billing dashboards, automated cost alerts, MOS study (F41).
