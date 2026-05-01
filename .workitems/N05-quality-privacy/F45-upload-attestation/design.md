---
feature_id: N05/F45
feature_type: domain
status: designed
hld_refs: ["HLD-§3.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — upload attestation excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F45 — Upload Attestation (No-PII Verification Gate)

## Overview

Adds a verification gate at the upload endpoint that requires the uploader to
attest that the document contains no personal identifying information beyond
what is necessary for exam accommodation. The attestation is logged and stored
alongside the upload metadata. Deferred to post-POC.

## biz_corpus

corpus_e_id: E11-F03
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [N01 upload pipeline]
- Adapter ports consumed: [StoragePort]
- External services: [Cloud Storage (HLD-§3.4), FastAPI upload handler]

## Design Elements

- DE-01: Upload API request body extended with `attested_no_pii: bool` field;
  FastAPI handler rejects uploads where field is false or absent (ref: HLD-§3.4)
- DE-02: Attestation record written to `manifests/{doc_id}/attestation.json`
  in GCS at upload time (ref: HLD-§3.4/StorageLayout)

## Approach

1. DE-01: Extend `POST /documents` request schema with required boolean field;
   HTTP 422 if missing or false.
2. DE-02: On accepted upload, write attestation record with timestamp, uploader
   ID (session token hash), and attestation flag to GCS.

## Decisions

- Client-side attestation only for v0; automated PII scan (e.g., DLP API) is future scope.
- Attestation record is subject to the same TTL as the document (F43).

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- HLD §12: whether to integrate Cloud DLP for automated scan — deferred to post-MVP.

## Risks

1. False attestations — mitigated by audit trail in GCS + DPIA process (F44).
2. Friction reducing adoption — mitigated by clear UI copy explaining why attestation is needed.
3. Attestation record subject to TTL deletion — note: attestation may need longer retention than document.

## Out of Scope

- Automated PII scanning, DLP integration, DPIA process (F44), no-PII logging (F46).
