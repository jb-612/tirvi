---
feature_id: N05/F39
feature_type: integration
status: designed
hld_refs: ["HLD-§5.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — quality benchmarks excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F39 — Baseline Quality Benchmark Harness v0

## Overview

Establishes a repeatable benchmark harness that runs the full OCR → NLP → TTS
pipeline against a held-out set of reference exam pages and records quality
metrics. This is the measurement foundation that all later quality-improvement
features (F40 MOS, F41 CI gates) depend on. Deferred to post-POC.

## biz_corpus

corpus_e_id: E10-F01
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [N01 OCR pipeline, N02 NLP pipeline, N03 TTS pipeline]
- Adapter ports consumed: [OCRBackend, TTSBackend]
- External services: [Cloud Storage (HLD-§3.4)]

## Design Elements

- DE-01: Benchmark runner script that loads reference pages from GCS, drives the
  full pipeline, and captures per-page word-error-rate and MOS proxy scores
  (ref: HLD-§5.4/FeedbackLoop)
- DE-02: Results store — benchmark output written as structured JSON to
  `bench/{run_id}/results.json` in GCS (ref: HLD-§3.4/StorageLayout)

## Approach

1. DE-01: Script reads held-out exam pages, runs OCR → NLP → TTS, diffs
   TTS transcript against reference transcript to compute WER.
2. DE-02: Serialise per-page metrics + aggregate summary to GCS under
   `bench/` prefix; print report to stdout.

## Decisions

- Language: Python (matches existing scripts/ tooling).
- No live retraining — results feed lexicon updates out-of-band (HLD-§5.4).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- HLD §12: held-out dataset curation not yet defined; stub accepts local TSV.

## Risks

1. Reference transcript availability — mitigated by synthetic stub for initial runs.
2. Pipeline latency makes CI integration slow — mitigated by sampling (F40 handles gating).
3. GCS costs for storing benchmark artifacts — mitigated by TTL lifecycle rule.

## Out of Scope

- Real MOS panel (F41), CI gating (F40), cost profiling (F42).
- Any UI for results visualisation.
