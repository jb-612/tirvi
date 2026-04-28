---
feature_id: F02-cloud-skeleton
status: approved
approved_at: 2026-04-29
prd_refs: []  # scaffolding — PRD scope: N/A
bounded_context: cloud-platform
---

# User Stories: F02 — Cloud skeleton

**Personas.** *Dani* — backend dev, runs `terraform plan` on PRs,
collaboration: paired with reviewer async. *Lior* — SRE / platform
engineer, owns prod rollouts and on-call, collaboration: reviewer +
solo apply. *Noa* — security engineer, audits IAM and secret access,
collaboration: async PR review.

## US-01: One-command env provisioning

**As** Dani **I want** `make tf-apply ENV=dev` to provision or update
the dev GCP environment from a clean checkout **so that** I can land
infra changes the same way I land code. PRD: N/A.

### Acceptance Criteria

- AC-01 (happy): `make tf-init ENV=dev && make tf-apply ENV=dev`
  succeeds on a clean GCP project; both Cloud Run services, all five
  Cloud Tasks queues, the bucket, and SAs exist.
- AC-02 (happy): Repeated `make tf-apply ENV=dev` is a no-op
  (deterministic IaC; `terraform plan` reports zero changes).
- AC-03 (edge): `make tf-apply` without `ENV=` exits non-zero with a
  message naming the missing var; default-env footgun is impossible.

### Notes

- Precedent: terraform-google-modules layouts.
- Error recovery: `make tf-destroy ENV=dev` cleanly tears down dev.

## US-02: Scale-to-zero by default; `min=1` opt-in

**As** Lior **I want** scale-to-zero on every Cloud Run service by
default, with `min-instances=1` as a per-service tfvar **so that**
prod cost stays low while latency-sensitive paths can opt in.
PRD: N/A.

### Acceptance Criteria

- AC-04 (happy): Default `dev.tfvars` produces both services with
  `min_instances = 0`; `prod.tfvars` overrides `worker.min_instances = 1`.
- AC-05 (happy): `--cpu-boost` is on for both services in both envs.
- AC-06 (edge): Setting `min_instances` in tfvars to a string instead
  of an int fails `terraform validate` with a clear type error.

### Notes

- Cost lever: scale-to-zero is the single biggest contributor to the
  $0.02/page target alongside the audio cache.

## US-03: Least-privilege IAM, audit-clean

**As** Noa **I want** every service to run under its own SA with the
narrowest IAM bindings that work **so that** a compromised key can't
read or write outside its scope. PRD: N/A.

### Acceptance Criteria

- AC-07 (happy): `gcloud asset analyze-iam-policy` against the dev
  project shows api SA has only `storage.objectAdmin` on the bucket,
  `cloudtasks.enqueuer`, and `secretAccessor` on its scoped keys —
  zero project-level roles.
- AC-08 (happy): Worker SA has only bucket-scoped objectAdmin and
  `secretAccessor` on TTS/DocAI keys.
- AC-09 (edge): Adding a project-level role to a SA in the IAM module
  fails the `terraform plan` CI check (custom OPA / sentinel rule).

### Notes

- Security model: assume-breach posture; IAM is the blast-radius cap.
- Precedent: SLSA / NIST 800-204 service-mesh IAM patterns.

## US-04: Plan-on-PR for safe rollouts

**As** Lior **I want** every PR touching `infra/terraform/` to post a
plan diff comment **so that** reviewers see the prod blast radius
before approving. PRD: N/A.

### Acceptance Criteria

- AC-10 (happy): A PR that adds a new Cloud Run env var triggers the
  GH Action; the resulting plan-diff comment lists exactly that change.
- AC-11 (edge): A PR that touches `tfstate` directly (mistake) is
  blocked at PR time with a status check failure.

### Notes

- The GH Action runs `terraform plan` against dev; prod plan is
  manual via `make tf-plan ENV=prod` after dev is approved.
