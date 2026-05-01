---
feature_id: N05/F44
feature_type: domain
status: designed
hld_refs: ["HLD-§3.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — DPIA process excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F44 — Data Protection Impact Assessment Process

## Overview

Documents and operationalises the DPIA for tirvi: inventories personal data
flows (exam PDFs containing student work), assesses risks, and defines
mitigations (TTL, no-PII logging, upload attestation). Produces a living DPIA
document and a checklist integrated into the release process. Deferred to
post-POC.

## biz_corpus

corpus_e_id: E11-F02
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [F43 TTL automation, F45 upload attestation, F46 no-PII logging]
- Adapter ports consumed: []
- External services: [Cloud Storage (HLD-§3.4)]

## Design Elements

- DE-01: DPIA document (`docs/privacy/dpia.md`) covering data inventory,
  lawful basis, risk matrix, and mitigation map (ref: HLD-§3.4)
- DE-02: DPIA checklist (`docs/privacy/dpia-checklist.md`) that gates each
  release — referenced in release runbook (ref: HLD-§3.4)

## Approach

1. DE-01: Author data inventory (what data, where stored, how long, who can
   access); map to GDPR/PDPA articles; assess residual risk after mitigations.
2. DE-02: Checklist items: TTL rules active, no-PII logging verified, upload
   attestation present, retention schedule reviewed.

## Decisions

- DPIA is a documentation-first feature (no runtime code); integration is via
  release process, not application code.
- Follows GDPR Article 35 structure as baseline; adapted for Israeli exam context.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- Regulatory jurisdiction (Israeli law vs. GDPR) — assumption: GDPR-aligned as conservative baseline.

## Risks

1. DPIA scope creep — mitigated by limiting to tirvi's own data flows (no third-party data processors).
2. Checklist not enforced — mitigated by adding DPIA checklist step to release runbook.
3. Regulatory changes — mitigated by dating the DPIA and scheduling annual review.

## Out of Scope

- Legal counsel review (external), runtime data-flow enforcement (F45, F46, F43).
