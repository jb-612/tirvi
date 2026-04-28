---
feature_id: F02-cloud-skeleton
feature_type: scaffolding
status: approved
mode: lite
approved_at: 2026-04-29
hld_refs: ["HLD-§7/DeploymentTopology", "HLD-§3.2/BackendAPI", "HLD-§3.3/Worker", "HLD-§3.4/StorageLayout", "HLD-§7.5/CostPosture"]
prd_refs: []  # scaffolding — PRD scope: N/A
adr_refs: ["ADR-012"]
bounded_context: cloud-platform
---

# Feature: F02 — Cloud skeleton (Cloud Run + Cloud Tasks + GCS + Terraform)

## Overview

Terraform-managed GCP plane that mirrors the dev compose topology in
production: two Cloud Run services (`tirvi-api`, `tirvi-worker`) sharing
one image, five Cloud Tasks queues for the per-stage pipeline, one GCS
bucket with lifecycle rules, Secret Manager wiring, and least-privilege
service accounts. Scale-to-zero by default; `min-instances=1` opt-in for
the OCR/NLP worker. `feature_type: scaffolding`. Lite mode.

## Dependencies

- Upstream features: F01 (image shape consumed by Cloud Run)
- Adapter ports consumed: none (ports arrive in F03)
- External services: GCP project, Terraform ≥ 1.7, gcloud SDK on dev/CI

## Interfaces

| Resource | Terraform module | Notes |
|----------|------------------|-------|
| `tirvi-api` (Cloud Run service) | `modules/cloud-run` | `--cpu-boost`, `min=0` default |
| `tirvi-worker` (Cloud Run service) | `modules/cloud-run` | same image; `min=1` opt-in |
| Cloud Tasks queues × 5 | `modules/cloud-tasks` | one per stage: ocr, normalize, nlp, plan, synthesize |
| `gs://tirvi-{env}` | `modules/storage` | lifecycle 24 h on pdfs/pages/plans/manifests; 30 d on audio |
| Secret Manager keys | `modules/secrets` | DocAI, Google TTS, Azure (added later) |
| Service accounts × 2 | `modules/iam` | api SA, worker SA |

## Approach

- **DE-01: TerraformLayout** — `infra/terraform/{envs/{dev,prod},modules/*}`
  with remote state in GCS, env-specific tfvars, deterministic plan
  output. (ref: HLD-§7/DeploymentTopology)
- **DE-02: CloudRunServices** — `tirvi-api` + `tirvi-worker`, same image,
  different entrypoints (env var `TIRVI_ROLE=api|worker`); scale-to-zero
  default; `min-instances=1` opt-in via tfvar; `--cpu-boost` always on.
  (ref: HLD-§3.2, HLD-§3.3, ADR-012)
- **DE-03: CloudTasksQueues** — one queue per pipeline stage so retries
  are isolated; per-queue rate caps configurable per env. Queues push to
  the worker URL with OIDC tokens. (ref: HLD-§7, research §3.2)
- **DE-04: GcsBucket** — single bucket per env (`tirvi-{env}`); lifecycle
  rule 24 h on `pdfs/`, `pages/`, `plans/`, `manifests/`; 30 d on
  `audio/`. Versioning off (object-store-as-DB pattern keeps it simple).
  (ref: HLD-§3.4/StorageLayout)
- **DE-05: SecretManagerWiring** — keys for DocumentAI, Google TTS,
  Azure (added when F28 lands) injected into Cloud Run as env-vars via
  Secret Manager. No keys in tfstate; access scoped to service accounts.
  (ref: HLD-§7 — Secret Manager)
- **DE-06: IamLeastPrivilege** — distinct SAs for api and worker. api SA:
  `storage.objectAdmin` on the bucket only, `cloudtasks.enqueuer`,
  `secretmanager.secretAccessor` on its scoped keys. worker SA: same
  bucket scope, `secretmanager.secretAccessor` on TTS/DocAI keys.
  No project-level roles. (ref: HLD-§7, security baseline)

## Decisions

- **D-01**: Compute primitive — Cloud Run vs. App Engine vs. Cloud
  Functions vs. GKE Autopilot → **ADR-012** (Accepted: Cloud Run
  services). Resolves the "GCP App Service" ambiguity from HLD §7.

Mechanical (no ADR): Terraform as IaC tool (industry default for GCP);
`tfstate` in GCS with versioning + locking via GCS object generation.

## Diagrams

- `docs/diagrams/F02-cloud-skeleton/gcp-topology.mmd` — services, queues,
  bucket, secrets, IAM bindings (explains DE-02..DE-06)
- `docs/diagrams/F02-cloud-skeleton/data-flow.mmd` — happy-path
  upload → enqueue → worker → audio sequence per HLD §9 (explains DE-02,
  DE-03, DE-04)

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | Faithful to HLD §3, §7 |

## HLD Open Questions

- **HLD §12 OQ#1** — confirm "GCP App Service" → Cloud Run — **resolved
  by ADR-012**.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Terraform drift between dev and prod envs | Medium | High | Single module set; envs differ only in tfvars; CI plan-on-PR |
| Cold-start kills 30 s p50 first-audio target | Medium | High | `min-instances=1` opt-in for worker during business hours; `--cpu-boost` |
| Service-account scope creep over time | Medium | High | IAM module is the only place SAs are minted; `gcloud asset analyze-iam-policy` audit in CI |
| `tfstate` corruption / lost lock | Low | Critical | GCS bucket-versioning on; remote-state docs in README |

## Out of Scope

- Application code in api/worker — F03 (ports), F05+ (real handlers)
- Cloud Tasks task payload schema — N01 (defined per stage)
- VPC / private networking — deferred (MVP uses default network)
- Multi-region — HLD §11 explicitly defers
- IAP / OAuth proxy on api — F33+ (auth lands in N04 / N05)
