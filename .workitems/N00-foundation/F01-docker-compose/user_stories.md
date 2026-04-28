---
feature_id: F01-docker-compose
status: approved
approved_at: 2026-04-28
prd_refs: []  # scaffolding — PRD scope: N/A
bounded_context: dev-platform
---

# User Stories: F01 — Single-Docker dev environment

**Personas.** *Dani* — backend dev, Python/FastAPI, 16 GB MacBook,
collaboration: solo + async PR review. *Mei* — frontend dev, Next.js,
8 GB laptop, collaboration: paired async with Dani. *Roni* — newcomer,
day 1, no Hebrew NLP background, collaboration: paired with Dani.

## US-01: One-command dev start

**As** Dani **I want** to bring up the full tirvi stack with a single
command on a fresh checkout **so that** I can iterate on api/worker code
without per-service mental overhead. PRD: N/A (scaffolding).

### Acceptance Criteria

- AC-01 (happy): `docker compose up` from repo root brings up web, api,
  worker, storage. All four healthchecks return green within 90 s.
- AC-02 (edge): If port 3000 / 8000 / 4443 is already in use, compose
  fails with a clear "port in use" error pointing at which service.
- AC-03 (edge): If Docker daemon isn't running, `make dev` prints a
  friendly "Docker daemon not reachable" message instead of a raw stack
  trace.

### Notes

- Precedent: claudeium uses `make smoke`; we mirror the shape.
- Error recovery: `docker compose down -v` cleans up without manual steps.
- Accessibility: terminal output is colour-blind safe (no red-on-green).

## US-02: Frontend-only mode for low-RAM machines

**As** Mei **I want** to skip the heavy NLP model sidecar **so that**
I can run web + api with mocked NLP responses without my laptop
swapping to disk. PRD: N/A.

### Acceptance Criteria

- AC-04 (happy): `docker compose up` (no profile) brings up
  web + api + worker + storage; api routes `/morph` and `/disambiguate`
  to a mock fixture.
- AC-05 (happy): `docker compose --profile models up` additionally
  starts the model sidecar; api routes the same paths to the live sidecar.
- AC-06 (edge): With models off, hitting an api route that requires the
  sidecar returns HTTP 503 with body explaining `models sidecar is
  profile-gated; restart with --profile models`.

### Notes

- Precedent: spaCy / Rasa model-server pattern.
- Memory floor: README documents 16 GB recommended; 8 GB OK without models.

## US-03: GCP overlay for production-path iteration

**As** Dani fixing a real-GCS bug **I want** to swap the fake server for
real GCS and the dev sidecar for the prod model image with one extra
flag **so that** I can reproduce a Cloud Run-only failure locally.
PRD: N/A.

### Acceptance Criteria

- AC-07 (happy): `docker compose -f docker-compose.yml -f compose.gcp.yml
  up` runs against real GCS (using host `GOOGLE_APPLICATION_CREDENTIALS`)
  and the production model image.
- AC-08 (edge): Without ADC mounted, api fails fast at startup with
  "no Google credentials found"; it does NOT silently fall back to fake-gcs.

### Notes

- Security: ADC mount is read-only; never copied into container layers.
- CI guard: only `make dev-gcp` invokes the overlay; default `make dev`
  excludes it to prevent accidental prod-credential usage in CI.

## US-04: Onboarding under 10 minutes

**As** Roni on day 1 **I want** a README block + one make target that
brings up the stack and runs a smoke test **so that** I can confirm my
machine is wired correctly before reading any code. PRD: N/A.

### Acceptance Criteria

- AC-09 (happy): `make dev-smoke` starts the stack, uploads a sample
  PDF, asserts api returns 200 on `GET /documents/{id}` with status
  `uploaded`, and exits 0 in ≤ 10 minutes wall-clock on a 16 GB MacBook.
- AC-10 (edge): If `tests/fixtures/sample-bagrut.pdf` is missing,
  `make dev-smoke` prints which file to add and exits 1.

### Notes

- Collaboration test: success means Roni runs `make dev-smoke` without
  asking Dani for help.
