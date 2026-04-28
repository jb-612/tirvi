---
feature_id: F01-docker-compose
status: approved
total_estimate_hours: 12
mode: lite
approved_at: 2026-04-28
amended_at: 2026-04-28  # +T-09 walking-skeleton, +T-10 smoke fixture
---

# Tasks: F01 — Single-Docker dev environment

Atomic tasks (≤ 2 h each), dependency-ordered, every task traced to a
Design Element + ≥ 1 Acceptance Criterion.

## T-01: Author Dockerfile.api (multi-stage Python)

- **DE:** DE-01 · **AC:** [AC-01] · **est:** 1.5h · **deps:** []
- test_file: `tests/dev/test_dockerfile_api.py`
- hints: stage 1 builder via `uv` or `poetry`; stage 2 `python:3.12-slim`. Bind-mount `api/` for hot reload.

## T-02: Author Dockerfile.web (Next.js dev)

- **DE:** DE-01 · **AC:** [AC-01] · **est:** 1h · **deps:** []
- test_file: `tests/dev/test_dockerfile_web.py`
- hints: `node:22-alpine`; `npm ci` then `npm run dev`. Bind-mount `web/`.

## T-03: Author Dockerfile.models (FastAPI sidecar)

- **DE:** DE-01 · **AC:** [AC-04, AC-05] · **est:** 1.5h · **deps:** []
- test_file: `tests/dev/test_dockerfile_models.py`
- hints: same Python base as api; pre-fetch weights at build for cache. Specific model is ADR-002 (deferred).

## T-04: Author docker-compose.yml (4 services + healthchecks)

- **DE:** DE-01 · **AC:** [AC-01, AC-02, AC-03] · **est:** 2h · **deps:** [T-01, T-02, T-09]
- test_file: `tests/dev/test_compose_default.py`
- hints: web/api/worker/storage. Named volume for fake-gcs. `depends_on: { service: { condition: service_healthy } }`.

## T-05: Add `--profile models` for sidecar

- **DE:** DE-02 · **AC:** [AC-04, AC-05, AC-06] · **est:** 1h · **deps:** [T-03, T-04]
- test_file: `tests/dev/test_compose_profiles.py`
- hints: `services.models.profiles: ["models"]`. api 503 with body explaining profile-gating when route hit without sidecar.

## T-06: Author compose.gcp.yml overlay

- **DE:** DE-03 · **AC:** [AC-07, AC-08] · **est:** 1h · **deps:** [T-04]
- test_file: `tests/dev/test_compose_gcp_overlay.py`
- hints: override `storage` (no-op); mount ADC read-only into api+worker. Fail fast on missing ADC.

## T-07: Bind-mount sources for hot reload

- **DE:** DE-04 · **AC:** [AC-01] · **est:** 0.5h · **deps:** [T-04]
- test_file: `tests/dev/test_hot_reload.py`
- hints: `volumes: ["./api:/app/api"]` on api; same shape for web.

## T-08: README dev-onboarding + `make dev-smoke`

- **DE:** DE-01, DE-02, DE-03 · **AC:** [AC-09, AC-10] · **est:** 1.5h · **deps:** [T-01..T-07, T-09, T-10]
- test_file: `tests/dev/test_dev_smoke.sh`
- hints: `make dev-smoke` runs default-profile compose, uploads `tests/fixtures/sample-bagrut.pdf`, asserts `GET /documents/{id}` status `uploaded`, `compose down -v`. README documents 16 GB floor + `make dev` / `make dev-gcp`.

## T-09: Walking-skeleton stubs (api/web/worker/models)

- **DE:** DE-05 · **AC:** [AC-01, AC-09] · **est:** 1.5h · **deps:** []
- test_file: `tests/dev/test_walking_skeleton.py`
- hints: `api/main.py` FastAPI with `GET /healthz` returning `{"ok": true}`; `worker/__main__.py` with proc-liveness loop; `models/main.py` FastAPI sidecar with `/healthz` (loads no weights yet); `web/` Next.js scaffold (default `npm run dev` is enough). All entry points respect ADR-002 deferral — model selection lands later. Pattern: Cockburn walking skeleton.

## T-10: Smoke fixture — synthetic 1-page Hebrew PDF

- **DE:** DE-05 · **AC:** [AC-09, AC-10] · **est:** 0.5h · **deps:** []
- test_file: `tests/dev/test_smoke_fixture.py`
- hints: `tests/fixtures/sample-bagrut.pdf` — one page, ≥ 4 lines of typeset Hebrew (Newsreader/David), one trivial English fragment, one number, ~50 KB. Generated via `weasyprint` from a `.html` source committed alongside; do NOT include real Bagrut content. Distinct from F13's curated 20-page benchmark.

## Dependency DAG

```
T-01,T-02,T-03 ─┐
T-09 ───────────┼──▶ T-04 ──▶ T-05,T-06,T-07 ──┐
                │                                ├──▶ T-08
T-10 ───────────┴────────────────────────────────┘
```

Total estimate: 1.5 + 1 + 1.5 + 2 + 1 + 1 + 0.5 + 1.5 + 1.5 + 0.5 = **12 h**
