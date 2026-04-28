---
feature_id: F02-cloud-skeleton
status: approved
total_estimate_hours: 13
mode: lite
approved_at: 2026-04-29
---

# Tasks: F02 — Cloud skeleton

Atomic tasks (≤ 2 h each), dependency-ordered, every task traced to a
Design Element + ≥ 1 Acceptance Criterion.

## T-01: Bootstrap `infra/terraform/` layout + remote state

- **DE:** DE-01 · **AC:** [AC-01, AC-02] · **est:** 1.5h · **deps:** []
- test_file: `tests/infra/test_tf_layout.py`
- hints: `infra/terraform/{envs/dev,envs/prod,modules/cloud-run,modules/cloud-tasks,modules/storage,modules/secrets,modules/iam}`. Backend: GCS bucket `tirvi-tfstate-{org}`, versioning on, locking via object generation.

## T-02: `modules/cloud-run` — service + cpu-boost + min_instances tfvar

- **DE:** DE-02 · **AC:** [AC-04, AC-05, AC-06] · **est:** 2h · **deps:** [T-01]
- test_file: `tests/infra/test_cloud_run_module.py`
- hints: variable `min_instances` type-pinned `number`; output the service URL. Annotation `run.googleapis.com/cpu-boost: "true"`. Image and `TIRVI_ROLE` env var are inputs.

## T-03: `modules/cloud-tasks` — 5 stage queues with rate caps

- **DE:** DE-03 · **AC:** [AC-01] · **est:** 1.5h · **deps:** [T-01]
- test_file: `tests/infra/test_cloud_tasks_module.py`
- hints: queue names `tirvi-{ocr,normalize,nlp,plan,synthesize}-{env}`. Per-queue `max_dispatches_per_second` and `max_concurrent_dispatches` as tfvars. OIDC service account ref to api SA.

## T-04: `modules/storage` — bucket + lifecycle rules

- **DE:** DE-04 · **AC:** [AC-01] · **est:** 1h · **deps:** [T-01]
- test_file: `tests/infra/test_storage_module.py`
- hints: `name = "tirvi-{env}"`, `uniform_bucket_level_access = true`, `versioning = false` (object-store-as-DB). Lifecycle: 24 h delete on prefixes `pdfs/, pages/, plans/, manifests/`; 30 d on `audio/`.

## T-05: `modules/secrets` — Secret Manager + per-key access

- **DE:** DE-05 · **AC:** [AC-01, AC-07, AC-08] · **est:** 1h · **deps:** [T-01]
- test_file: `tests/infra/test_secrets_module.py`
- hints: secrets `tirvi-docai-key`, `tirvi-tts-key`. Access policy keyed by SA email; no project-level grant. Output secret names for env-var injection in T-02.

## T-06: `modules/iam` — service accounts + scoped role bindings

- **DE:** DE-06 · **AC:** [AC-07, AC-08, AC-09] · **est:** 1.5h · **deps:** [T-04, T-05]
- test_file: `tests/infra/test_iam_module.py`
- hints: SAs `tirvi-api-{env}`, `tirvi-worker-{env}`. Bucket-scoped `storage.objectAdmin` (NOT project-level). `cloudtasks.enqueuer` on api SA. `secretAccessor` keyed per secret. Add OPA/Sentinel rule blocking project-level role bindings.

## T-07: `envs/dev` + `envs/prod` tfvars + module wiring

- **DE:** DE-01 · **AC:** [AC-01, AC-04] · **est:** 1.5h · **deps:** [T-02..T-06]
- test_file: `tests/infra/test_envs.py`
- hints: dev: both services `min_instances = 0`. prod: `worker.min_instances = 1` (business-hour latency). Region default `me-west1`; project IDs from env. Backend prefix `envs/{name}`.

## T-08: GitHub Actions `terraform-plan.yml` for plan-on-PR

- **DE:** DE-01 · **AC:** [AC-10, AC-11] · **est:** 1h · **deps:** [T-07]
- test_file: `.github/workflows/__test__/test_tf_plan_action.yml`
- hints: workload-identity-federation auth (no JSON keys); plan against dev; post diff as PR comment. Block PRs that touch `*.tfstate*` paths via path filter + status check.

## T-09: README + `make tf-init / tf-plan / tf-apply / tf-destroy`

- **DE:** DE-01 · **AC:** [AC-01, AC-03] · **est:** 1h · **deps:** [T-01..T-08]
- test_file: `tests/infra/test_makefile_targets.sh`
- hints: targets require `ENV=dev|prod`; missing → exit 2 with usage. README documents bootstrap (project create, APIs enable, tfstate bucket), workload-identity-federation setup, and the SLSA-style audit-clean checklist.

## Dependency DAG

```
T-01 ──▶ T-02, T-03, T-04, T-05 ──▶ T-06 ──▶ T-07 ──▶ T-08 ──▶ T-09
```

Total estimate: 1.5 + 2 + 1.5 + 1 + 1 + 1.5 + 1.5 + 1 + 1 = **12 h**
(plus ~1 h slack for plan-cycle iteration → 13 h budget)
