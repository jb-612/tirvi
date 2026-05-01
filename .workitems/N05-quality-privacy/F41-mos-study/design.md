---
feature_id: N05/F41
feature_type: integration
status: designed
hld_refs: ["HLD-§5.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — MOS listening study excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F41 — Mean Opinion Score Listening Study

## Overview

Runs a structured MOS listening study in which human raters score synthesised
Hebrew audio samples on a 1–5 scale. Results are ingested into the benchmark
store to complement automated WER metrics. Deferred to post-POC.

## biz_corpus

corpus_e_id: E10-F03
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [F39 benchmark harness]
- Adapter ports consumed: [TTSBackend]
- External services: [Cloud Storage (HLD-§3.4), survey tool TBD]

## Design Elements

- DE-01: Study runner script that exports a sample set of TTS audio clips and
  a rating form; ingests completed ratings CSV (ref: HLD-§5.4/FeedbackLoop)
- DE-02: MOS aggregation module that computes per-voice and per-page MOS from
  ratings CSV and writes to `bench/{run_id}/mos.json` in GCS (ref: HLD-§5.4)

## Approach

1. DE-01: Script samples N audio clips from pipeline output, packages them with
   a rating sheet template (Google Form or CSV); study coordinator distributes.
2. DE-02: After rating session, ingest ratings CSV → compute mean + CI →
   append to benchmark results.

## Decisions

- Manual survey distribution for v0; automation (Mechanical Turk etc.) is future scope.
- MOS format follows ITU-T P.800 5-point scale.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- HLD §12: rater pool definition (internal vs. external) TBD.

## Risks

1. Rater availability — mitigated by keeping initial study small (20 clips).
2. Rater bias from Hebrew proficiency variation — mitigated by screening.
3. Subjectivity of MOS — mitigated by using aggregate mean + confidence interval.

## Out of Scope

- Automated MOS proxies (handled in F39), CI gating (F40), cost profiling (F42).
