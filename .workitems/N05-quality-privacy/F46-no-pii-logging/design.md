---
feature_id: N05/F46
feature_type: domain
status: designed
hld_refs: ["HLD-§3.4"]
prd_refs: []
adr_refs: []
deferred: true
deferred_reason: "Post-POC — no-PII logging guard excluded from POC scope per PLAN-POC.md §Deferred"
---

# Feature: F46 — No-PII Logging Guard (Structured Log Scrubber)

## Overview

Adds a structured logging middleware that scrubs potential PII fields (student
name, file paths containing student identifiers, document text excerpts) from
all log lines before they are emitted to Cloud Logging. Prevents exam content
from appearing in operational logs. Deferred to post-POC.

## biz_corpus

corpus_e_id: E11-F04
biz_status: deferred
biz_notes: "User stories TBD — biz-functional-design not yet run for N05."

## Dependencies

- Upstream features: [N01 upload pipeline, N02 NLP pipeline]
- Adapter ports consumed: []
- External services: [Cloud Logging]

## Design Elements

- DE-01: Log scrubber middleware (Python logging Filter subclass) that strips
  or masks values for a configurable set of sensitive keys (e.g., `text`,
  `transcript`, `filename`) from structured log records (ref: HLD-§3.4)
- DE-02: Allowlist / denylist configuration (`logging/scrub_config.yaml`)
  versioned in repo; middleware reads at startup (ref: HLD-§3.4)

## Approach

1. DE-01: Implement `PiiScrubFilter(logging.Filter)` that walks log record
   `extra` dict and replaces sensitive key values with `[REDACTED]`.
2. DE-02: `scrub_config.yaml` lists sensitive keys and regex patterns; loaded
   at app startup; hot-reload not required for v0.

## Decisions

- Regex-based scrubbing chosen over ML-based NER for determinism and zero latency overhead.
- Applied at the logging layer, not at source, to avoid changing call sites.

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | —         |

## HLD Open Questions

- HLD §12: Cloud DLP integration for log scrubbing — deferred; regex sufficient for v0.

## Risks

1. Incomplete scrubbing if new PII-bearing keys added without updating allowlist — mitigated by periodic config review.
2. Over-scrubbing making logs undebuggable — mitigated by preserving non-PII structural context (doc_id hash, stage name).
3. Performance: regex on every log record — mitigated by compiling patterns at startup.

## Out of Scope

- ML-based PII detection, Cloud DLP, DPIA process (F44), upload attestation (F45).
