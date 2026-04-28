---
feature_id: F01-docker-compose
feature_type: scaffolding
status: approved
mode: lite
approved_at: 2026-04-28
hld_refs: ["HLD-§8/SingleContainerDev", "HLD-§12-OQ2/ComposeVsSupervisord"]
prd_refs: []  # scaffolding — PRD scope: N/A
adr_refs: ["ADR-011"]
bounded_context: dev-platform
---

# Feature: F01 — Single-Docker dev environment

## Overview

One `docker compose up` brings the full tirvi stack up locally for
development: frontend, API, worker, NLP model sidecar, and a fake-GCS
server. A compose profile gates the heavy NLP sidecar so a frontend
developer on a 8 GB machine isn't forced to load Hebrew NLP weights.

`feature_type: scaffolding`. Pure infrastructure; no domain logic. Lite
mode: solo design + self-review (no meeting room, no R1/R2).

## Dependencies

- Upstream features: none
- Adapter ports consumed: none (the ports themselves arrive in F03)
- External services: Docker Engine ≥ 24, Compose v2

## Interfaces

| Service | Host port | Healthcheck | Hot reload |
|---------|-----------|-------------|------------|
| `web` (Next.js dev) | 3000 | `GET /` | yes (volume) |
| `api` (FastAPI --reload) | 8000 | `GET /healthz` | yes (volume) |
| `worker` (same image, alt entrypoint) | — | proc liveness | yes |
| `models` (FastAPI sidecar) | 8001 | `GET /healthz` | no (model load is slow) |
| `storage` (fake-gcs-server) | 4443 | `GET /storage/v1/b` | n/a |

The `models` sidecar exposes `/morph` and `/disambiguate` (consumed by
the NLP backbone shipped in N02). Specific model weights are decided by
**ADR-002** (deferred); F01 is mode-agnostic and just stands up the
sidecar shape.

## Approach

- **DE-01: ComposeStack** — single `docker-compose.yml` declaring all
  five services with named networks, volumes, healthchecks, and
  `depends_on: condition: service_healthy` ordering.
  (ref: HLD-§8/SingleContainerDev)
- **DE-02: ProfileGuards** — `--profile models` gates the heavy NLP
  sidecar. Default `up` runs web + api + worker + storage with api
  routing `/morph` and `/disambiguate` to a mock fixture. With the
  profile active, api routes to the live sidecar.
  (ref: HLD-§8 — clarified by research §6 "16 GB dev floor")
- **DE-03: GcpOverlay** — `compose.gcp.yml` overlay swaps `storage` for
  real GCS (Application Default Credentials mounted read-only) and
  `models` for the production sidecar entrypoint.
  Use: `docker compose -f docker-compose.yml -f compose.gcp.yml up`.
  (ref: HLD-§8 — Optional `compose.gcp.yml` overlay)
- **DE-04: HotReloadMounts** — host bind-mounts for `web/` and `api/`
  source directories enable Next.js + FastAPI hot reload without rebuild.
  The `models` sidecar is rebuilt on demand only.
- **DE-05: WalkingSkeleton** — minimal app stubs (`api/main.py`,
  `worker/__main__.py`, `models/main.py`, Next.js index page) each
  expose `/healthz` (or equivalent) so the smoke contract (AC-01, AC-09)
  is exercisable end-to-end before any real feature code lands. Pattern:
  Cockburn / *Growing OO Software, Guided by Tests*. F03 later
  restructures `api/` around the adapter ports; the entry points stay.
  (ref: HLD-§8 — implicit; required for the smoke target to be honest)

## Decisions

- **D-01**: Multi-service Compose project vs. single image with process
  supervisor (`supervisord`) → **ADR-011** (Accepted: Compose).
  HLD §8 prefers Compose; ADR-011 documents rationale + alternatives.

## Diagrams

- `docs/diagrams/F01-docker-compose/topology.mmd` — services, ports,
  dependency edges (explains DE-01, DE-02, DE-03)
- `docs/diagrams/F01-docker-compose/boot-order.mmd` — sequence of
  startup, healthcheck ordering, profile-gated services (explains DE-01)

## HLD Deviations

| Element | Deviation | Rationale |
|---------|-----------|-----------|
| —       | —         | Faithful to HLD §8 |

## HLD Open Questions

- **HLD §12 OQ#2** — compose vs. supervisord — **resolved by ADR-011**.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Model sidecar OOM on 8 GB dev laptop | Medium | High (DX) | `--profile models` opt-in; document 16 GB floor in README |
| `fake-gcs-server` drift from real GCS API | Low | Medium | Pin version; nightly CI smoke against real GCS |
| `compose.gcp.yml` accidentally used in CI | Low | High | Default profile excludes it; explicit `make` targets only |

## Out of Scope

- Production Cloud Run Terraform — F02
- Adapter port code — F03
- CI gates wiring — F04
- Build of AlephBERT/DictaBERT weight cache — F17 / model image build
