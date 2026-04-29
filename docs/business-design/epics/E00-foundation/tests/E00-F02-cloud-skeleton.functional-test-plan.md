# E00-F02 — Cloud Skeleton: Functional Test Plan

## Scope
Verifies Terraform produces correct GCP topology (Cloud Run × 2, 5 Cloud Tasks
queues, GCS bucket with lifecycle rules, IAM, Secret Manager). Out of scope:
business logic on Cloud Run, queue throughput tuning beyond skeleton defaults.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E00-F02-S01 | Apply infrastructure for a new environment | Critical |
| E00-F02-S02 | Cloud Tasks per-stage queue isolates retries | High |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| `tirvi-{env}` bucket | infra | S01 | exists with prefix-scoped lifecycle |
| Cloud Run services | infra | S01 | `tirvi-api` (min=0|1), `tirvi-worker` (min=0|1) |
| Cloud Tasks queues | infra | S02 | five queues with isolated retry budgets |
| Secret Manager secrets | infra | S01 | TTS/OCR keys readable by service account only |

---

## Test Scenarios

### FT-006: Apply from clean state in ≤ 15 minutes
**Related stories:** E00-F02-S01
**Preconditions:** empty GCP project; APIs enabled
**Input:** `terraform apply -auto-approve`
**Expected output:** all listed resources present; outputs printed
**Validation method:** `terraform output` + `gcloud` describe per resource
**Priority:** Critical

### FT-007: Lifecycle rule applies to PDFs but not audio
**Related stories:** E00-F02-S01
**Input:** inspect bucket lifecycle config
**Expected output:** prefix `pdfs/`, `pages/`, `plans/`, `manifests/` carry 24h TTL; `audio/` has none
**Priority:** Critical

### FT-008: Per-queue retry isolation
**Related stories:** E00-F02-S02
**Input:** flood `synthesize` queue to limit; observe `ocr` queue
**Expected output:** `ocr` continues with own concurrency cap; no cross-stage starvation
**Priority:** High

### FT-009: Secrets unreadable by non-runtime principals
**Related stories:** E00-F02-S01
**Input:** developer-role principal calls `secretmanager.versions.access`
**Expected output:** PERMISSION_DENIED
**Priority:** Critical

### FT-010: Re-apply is idempotent
**Related stories:** E00-F02-S01
**Input:** run `terraform apply` twice with no changes
**Expected output:** "No changes" on second run
**Priority:** High

## Negative Tests
- Apply to project without billing → fails with clear message.
- Apply with conflicting bucket name → fails before any IAM is changed.

## Boundary Tests
- Lifecycle TTL set to 0 (immediate delete) — Terraform plan refuses unless
  ADR-005-lite waiver applied.
- Cloud Run `min-instances` = 0 in dev, = 1 in prod — workspace-keyed.

## Permission and Role Tests
- TF service account requires no project-Owner; uses least-priv role bundle.
- Runtime SA only has `storage.objectViewer/Creator` on `tirvi-{env}`.

## Integration Tests
- Cloud Tasks → Cloud Run worker URL: HTTP signed-OIDC token contract.
- Cloud Run → GCS: ADC-based access.
- Cloud Run → Secret Manager: at-runtime fetch.

## Audit and Traceability Tests
- TF state versioned in remote backend.
- Every resource has `env` and `feature` labels for billing breakdown.

## Regression Risks
- Adding Cloud SQL post-MVP must not break existing TF state.
- Bucket rename (e.g., `tirvi-{env}` → `tirvi-{env}-{region}`) breaks lifecycle
  history; requires ADR.

## Open Questions
- Does each environment need a separate KMS key or single shared key?
