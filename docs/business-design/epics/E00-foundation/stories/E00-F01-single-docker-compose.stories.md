# E00-F01 — Single-Docker Compose Dev Environment

## Source Basis
- PRD: §4 Goal 6 (single Docker container), §9 (Single Docker dev environment)
- HLD: §8 Single-container dev environment, §12 OQ#2
- Research: src-003 §3 change 6 (16 GB floor), §10 Phase 0 F0.1
- Assumptions: ASM08 (compose, not supervisor)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P04 Operator/SRE | maintains dev env | one-command bring-up | model weights consume RAM | `docker compose up` works on 16 GB laptop |
| P08 Backend Dev | builds adapters | edit-and-reload loop | slow model load on every restart | API hot-reload < 2 s; models stay warm |
| P09 Frontend Dev | builds UI | run web only | doesn't need model weights | `--profile models` opt-in |

## Collaboration Model
1. Primary: backend developer running pipeline-touching code.
2. Supporting: frontend dev (web-only), SRE (image hygiene).
3. System actors: `web`, `api`, `worker`, `models`, `fake-gcs-server`.
4. Approvals: none (local dev).
5. Handoff: image lineage tagged for parity with prod base image.
6. Failure recovery: `docker compose down -v` reset; cached weights re-mounted.

## Behavioural Model
1. Hesitation: dev unsure whether to start `models` profile.
2. Rework: forgets `--profile models`, sees connection refused, retries.
3. Partial info: `.env` missing GCP credentials, falls back to fakes.
4. Abandoned flow: laptop swaps, dev kills compose mid-startup.
5. Retry: model server crashes on OOM; restart with smaller batch.

---

## User Stories

### Story 1: Bring up full stack in one command

**As a** backend developer
**I want** `docker compose up` to start web + api + worker + models + fake-gcs
**So that** I can develop the OCR→TTS pipeline locally without GCP credentials.

#### Preconditions
- Docker ≥ 24, Compose ≥ 2.20, ≥ 16 GB RAM available.

#### Main Flow
1. `git clone tirvi && cd tirvi && docker compose up`
2. Compose pulls/builds five services; model service warms AlephBERT weights.
3. `web` exposes :3000, `api` :8080, `models` :8001, `fake-gcs` :4443.
4. Health check endpoints all return 200 within 90 s.
5. Developer opens http://localhost:3000 and uploads a sample PDF.

#### Alternative Flows
- Run `docker compose --profile models up` opt-in if profile gating active.
- Run without `models` for frontend-only work; `api` returns mocked responses.

#### Edge Cases
- 16 GB host with browsers open: model service OOMs; surfaced via health check.
- `fake-gcs-server` port collision; compose fails fast with clear error.

#### Acceptance Criteria
```gherkin
Given a clean clone on a 16 GB Linux/macOS host
When a developer runs `docker compose up`
Then within 90 seconds all services report healthy
And uploading a sample PDF produces a playable first block within 60 s
```

#### Dependencies
- DEP-EXT-Docker (≥ 24)
- DEP-EXT-DictaBERT weights (cached volume)

#### Non-Functional Considerations
- Performance: warm-restart of `api` ≤ 2 s (model server stays running).
- Reliability: stage failures isolated; no cross-service cascade.
- Accessibility: N/A (dev-only).
- Security: no real GCP creds required by default.

#### Open Questions
- Do we ship pre-baked model weights in the image, or download on first run?

---

### Story 2: Frontend-only profile without model weights

**As a** frontend developer
**I want** to run `web` plus a mocked API without spinning up the NLP service
**So that** I can iterate on the player UI on a 8 GB laptop.

#### Preconditions
- `MOCK_API=1` env var or `--profile lite` documented.

#### Main Flow
1. Developer runs `docker compose --profile lite up web api-mock fake-gcs`.
2. `api-mock` returns canned `plan.json` and `audio.mp3` from fixtures.
3. `web` renders the player using the mocked content.

#### Edge Cases
- Mock fixtures stale vs. real `plan.json` schema; CI lint catches drift.

#### Acceptance Criteria
```gherkin
Given the lite profile is selected
When the developer runs `docker compose --profile lite up`
Then `web` renders the player with cached fixtures within 30 seconds
And no model weights are loaded into memory
```

#### Dependencies
- DEP-INT-fixtures (E00-F03 adapter fakes seed the fixtures)

#### Non-Functional Considerations
- Performance: TTI < 5 s on lite stack.
- Resource: peak resident < 4 GB.

#### Open Questions
- Should `lite` ship as default for `dev` setup docs, or as opt-in?
