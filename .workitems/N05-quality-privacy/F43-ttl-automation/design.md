---
feature_id: N05/F43
feature_type: integration
status: designed
hld_refs: ["HLD-§3.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — TTL automation excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F43 — Draft TTL Automation (Expiry + Cleanup)

## Overview

Implements automated object lifecycle management for the GCS bucket: applies
TTL rules to auto-delete `pdfs/`, `pages/`, `plans/`, and `manifests/` after
the configured TTL (default 7 days). `audio/` objects are excluded because
they are content-addressed and shareable. Deferred to post-POC.

## biz_corpus

corpus_e_id: E11-F01
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [N01 upload pipeline]
- Adapter ports consumed: []
- External services: [Cloud Storage lifecycle rules (HLD-§3.4)]

## Design Elements

- DE-01: GCS bucket lifecycle rule configuration (Terraform or gcloud CLI)
  that deletes objects under `pdfs/`, `pages/`, `plans/`, `manifests/`
  prefixes after 7 days (ref: HLD-§3.4/StorageLayout)
- DE-02: Cleanup verification script that lists objects approaching TTL
  and confirms lifecycle rule is active (ref: HLD-§3.4)

## Approach

1. DE-01: Apply `lifecycle_rule` to bucket in Terraform or gcloud storage
   buckets update; scoped to listed prefixes only; `audio/` excluded.
2. DE-02: Script queries GCS metadata for objects older than TTL - 1 day
   and emits a report; intended for operational spot-checks.

## Decisions

- 7-day TTL confirmed as default per HLD-§3.4 open question #3.
- `audio/` excluded from TTL because content-hash keying makes it safe to share across users.
- GCS native lifecycle rules preferred over Cloud Functions for zero-maintenance.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- HLD §12 OQ #3 (7-day TTL default) — adopted as-is.

## Risks

1. Accidental deletion of audio objects — mitigated by scoping rules to explicit prefixes.
2. TTL too short for long-running exams — mitigated by making TTL configurable per environment.
3. Lifecycle rule propagation delay in GCS (up to 24h) — documented in runbook.

## Out of Scope

- Per-user TTL customisation, DPIA process (F44), upload attestation (F45).
