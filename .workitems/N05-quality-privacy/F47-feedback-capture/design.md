---
feature_id: N05/F47
feature_type: domain
status: designed
hld_refs: ["HLD-§5.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — feedback capture excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F47 — User Feedback Capture for Lexicon/Quality Improvements

## Overview

Exposes a `POST /documents/{id}/feedback` endpoint through which users can
report a mispronounced word or wrong reading. Feedback records are stored in
GCS under `feedback/{doc_id}/{ts}.json` and feed the lexicon update and
evaluation-set pipeline out-of-band. No live retraining in MVP.
Deferred to post-POC.

## biz_corpus

corpus_e_id: E11-F05
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [N03 TTS pipeline, N01 upload pipeline]
- Adapter ports consumed: [StoragePort]
- External services: [Cloud Storage (HLD-§3.4, §5.4), FastAPI handler]

## Design Elements

- DE-01: `POST /documents/{id}/feedback` FastAPI endpoint accepting a JSON
  body with `word`, `page`, `expected_pronunciation` fields; validates and
  stores to GCS (ref: HLD-§5.4/FeedbackLoop)
- DE-02: Feedback record written to `feedback/{doc_id}/{ts}.json` in GCS;
  subject to separate (longer) TTL than document objects (ref: HLD-§3.4/StorageLayout)

## Approach

1. DE-01: FastAPI route validates request body schema, rejects empty/malformed
   input, writes the record to GCS via StoragePort.
2. DE-02: GCS key uses ISO timestamp to avoid collision; feedback/ prefix
   excluded from 7-day TTL lifecycle rule (F43).

## Decisions

- Feedback stored as raw JSON; no aggregation or deduplication in MVP.
- `feedback/` prefix excluded from short TTL to preserve quality signal.
- No live retraining — corrections feed lexicon updates out-of-band (HLD-§5.4).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- HLD §12: feedback retention policy TBD; assumption: 90 days default.

## Risks

1. Feedback spam / abuse — mitigated by rate limiting on the endpoint.
2. Feedback volume overwhelming manual lexicon review — mitigated by batching review sessions.
3. Feedback TTL mismatch with document TTL — mitigated by explicit exclusion of `feedback/` from F43 rules.

## Out of Scope

- Automated lexicon update pipeline, live retraining, feedback UI (beyond API).
