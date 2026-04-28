---
adr_id: ADR-011
title: Dev container layout — Compose vs. supervisord
status: Accepted
date: 2026-04-28
deciders: [tirvi research, F01-docker-compose]
bounded_context: dev-platform
hld_refs: ["HLD-§8/SingleContainerDev", "HLD-§12-OQ2/ComposeVsSupervisord"]
related_features: [F01-docker-compose]
related_adrs: []
---

# ADR-011 — Dev container layout: Compose vs. supervisord

## Status

**Accepted** (2026-04-28). Resolves HLD §12 OQ#2.

## Context

The PRD requires "the entire dev environment in a single Docker container."
HLD §8 reads this as one of two shapes:

1. **Multi-service Compose project** — one `docker compose up`, five
   services (web, api, worker, models, storage), shared network,
   one process per container.
2. **Single image with process supervisor** — one `docker run`, all
   services running as subprocesses of `supervisord` (or `s6-overlay`)
   inside one container.

Both honor the literal "single command" requirement. They differ on
isolation, hot-reload semantics, debuggability, memory ceiling, and
production parity (Cloud Run is one-process-per-container).

## Decision

Use **multi-service Compose project**. The model sidecar lives in its
own container, gated behind `--profile models`. A `compose.gcp.yml`
overlay swaps the fake-GCS container for real GCS in production-path
testing.

## Consequences

**Positive**

- Each service has its own image, file watchers, and crash boundary.
  Hot-reload on `api` doesn't restart the model sidecar (which costs
  ~30–60 s of weight load).
- Memory ceiling is per-service, not per-machine. Frontend devs on 8 GB
  laptops opt out of models cleanly via the `models` profile.
- Logs are per-service via `docker compose logs <svc>` — no
  `supervisord` log multiplexing or color stripping.
- Production parity: Cloud Run also runs one process per container.

**Negative**

- "Single Docker container" interpretation is permissive — strict readers
  may push back. Counter: HLD §8 explicitly endorses Compose; the literal
  reading was never the intent.
- Compose v2 is a hard dependency on dev machines.

## Alternatives

**A1: Single image with `supervisord`** (rejected)

- Pros: one `docker run`; satisfies the most literal PRD reading; no
  Compose dependency.
- Cons: hot-reload is fragile (signal handling, partial restarts); logs
  multiplex; memory ceiling is per machine; weight reload on every code
  change kills DX. Cloud Run target is per-process anyway.

**A2: Single image with `s6-overlay` + `tini`** (rejected)

- Same drawbacks as A1; slightly cleaner process management. Still
  conflates concerns and breaks hot-reload.

## References

- HLD §8 (Single-container dev environment)
- HLD §12 OQ#2 (compose vs. supervisord)
- `.workitems/N00-foundation/F01-docker-compose/`
- Prior art: claudeium project's `make smoke` on Compose
