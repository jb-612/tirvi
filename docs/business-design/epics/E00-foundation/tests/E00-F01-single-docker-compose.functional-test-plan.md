# E00-F01 — Single-Docker Compose: Functional Test Plan

## Scope
Verifies the dev environment composes, hot-reloads, exposes documented ports,
and routes between services. Out of scope: GCP credential paths, prod CD.

## Source User Stories
| Story ID | Title | Priority |
|----------|-------|---------|
| E00-F01-S01 | Bring up full stack in one command | Critical |
| E00-F01-S02 | Frontend-only profile | High |

## Functional Objects Under Test
| Object | Type | Related Story | Expected Behaviour |
|--------|------|--------------|-------------------|
| compose graph | platform | S01 | brings up 5 services with healthchecks |
| `--profile lite` | configuration | S02 | excludes `models`, `worker`; uses fixture API |
| service health endpoints | platform | S01 | return 200 within 90 s |

---

## Test Scenarios

### FT-001: Cold compose-up reaches healthy in 90 s
**Related stories:** E00-F01-S01
**Preconditions:** clean docker volumes; 16 GB host
**Input:** `docker compose up -d`
**Expected output:** `docker compose ps` shows all 5 services healthy
**Validation method:** healthcheck assertions + readyz probes
**Failure mode:** any service unhealthy → fail
**Priority:** Critical

### FT-002: Hot reload keeps model server warm
**Related stories:** E00-F01-S01
**Preconditions:** stack running
**Input:** edit `api/main.py`; save
**Expected output:** `api` restarts < 2 s; `models` PID unchanged
**Validation method:** poll `models` PID before/after
**Priority:** High

### FT-003: Lite profile boots without model weights
**Related stories:** E00-F01-S02
**Preconditions:** clean state
**Input:** `docker compose --profile lite up -d`
**Expected output:** `web`, `api-mock`, `fake-gcs` running; `models` not present
**Priority:** High

### FT-004: Stage failure isolates per service
**Related stories:** E00-F01-S01
**Preconditions:** stack running
**Input:** `docker stop <models>`
**Expected output:** `api` stays healthy; pipeline stages return typed `MODELS_UNAVAILABLE`
**Priority:** High

### FT-005: Sample PDF produces first audio block in ≤ 60 s
**Related stories:** E00-F01-S01
**Preconditions:** stack healthy; sample PDF in fixtures
**Input:** upload `samples/exam-5p.pdf`
**Expected output:** first block audio playable in ≤ 60 s
**Priority:** Critical

## Negative Tests
- No Docker daemon → compose fails fast with actionable message.
- Port 3000 in use → compose surfaces port conflict, exits non-zero.
- Insufficient memory (8 GB) → `make doctor` emits FAIL prior to compose.

## Boundary Tests
- 16 GB exact (no headroom): models start but warn on low RAM.
- 32 GB: all services + browser tabs co-exist.

## Permission and Role Tests
- Non-Docker-group user on Linux: compose fails with permission hint.

## Integration Tests
- Cross-service routing: `web` → `api` → `worker` → `fake-gcs` round-trip on
  upload + status poll.
- `models` ↔ `worker` gRPC/HTTP contract honored on schema upgrade.

## Audit and Traceability Tests
- Compose generates a run-id label per service for log correlation.

## Regression Risks
- Adding a sixth service (e.g., redis for E11 corrections) without updating
  doctor / lite-profile docs.
- Compose v2 → v3 migration breaks profile semantics.

## Open Questions
- Should fixture PDFs ship in repo or be downloaded on first `up`?
