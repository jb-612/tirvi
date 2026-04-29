# E00-F05 — 16 GB Dev Floor & Compose Profile Gating

## Source Basis
- HLD: §8 Single-container dev environment
- Research: src-003 §3 change #6 (16 GB floor; `--profile models`), §10 Phase 0 F0.5
- Assumptions: ASM08 (compose-with-profiles preferred over supervisor)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P09 Frontend Dev | works on player UI | run web on 8 GB laptop | model weights blow RAM | `--profile models` opt-in |
| P08 Backend Dev | works on NLP / TTS | full stack with weights warm | OOM under all-services-up | docs prescribe 16 GB floor |
| P04 SRE | onboards new devs | predictable resource budget | varying laptops | `make doctor` reports compliance |

## Collaboration Model
1. Primary: developer onboarding.
2. Supporting: SRE maintaining the doctor script; team-lead documenting the floor.
3. System actors: `make doctor`, `docker stats`, compose profile resolver.
4. Approvals: resource floor change → ADR-010 slot.
5. Handoff: onboarding doc → first-day task.
6. Failure recovery: dev with 8 GB is auto-routed to lite profile.

## Behavioural Model
- Hesitation: dev unsure whether their MacBook can run `models`.
- Rework: dev runs without profile; pipeline returns 503; dev re-reads docs.
- Partial info: dev has 16 GB but four browsers; OOM guidance points to closing apps.
- Retry: `make doctor` re-run after closing apps confirms resource availability.

---

## User Stories

### Story 1: `make doctor` reports dev resource health

**As a** new developer
**I want** a single `make doctor` command that confirms my laptop meets the dev floor
**So that** I don't waste an hour chasing OOM errors on day one.

#### Preconditions
- Repository contains `make doctor` target invoking shell + compose introspection.

#### Main Flow
1. `make doctor` runs.
2. Reports: total RAM, free RAM, Docker memory budget, available disk, Compose version, Python version.
3. Compares to required floor (16 GB total / 12 GB Docker budget / 20 GB disk).
4. Prints PASS/FAIL with per-line reasons.

#### Alternative Flows
- On FAIL: prints "use `--profile lite`" recommendation and links to lite profile docs.

#### Edge Cases
- Apple Silicon: warns about Rosetta penalty for x86 model containers.
- Linux: cgroup limits override container memory budget; doctor reads cgroup config.

#### Acceptance Criteria
```gherkin
Given a developer is on a 16 GB host with Docker memory set to 12 GB
When they run `make doctor`
Then the output reports PASS for memory, disk, and runtime versions
And a clear next-step pointer to `docker compose up`
```

#### Dependencies
- DEP-INT to E00-F01 (compose), E00-F03 (lite-profile fixtures)

#### Non-Functional Considerations
- DX: doctor runs in ≤ 10 s.
- Reliability: doctor passes offline.

#### Open Questions
- Should doctor also run on CI as a sanity check?

---

### Story 2: `--profile models` opt-in keeps light workflows light

**As a** frontend developer
**I want** the model service excluded from `docker compose up` unless I opt in
**So that** I can run player UI work with < 4 GB resident.

#### Preconditions
- Compose file uses profile-tagged services.

#### Main Flow
1. Default `docker compose up` brings up `web`, `api`, `worker`, `fake-gcs` (no `models`).
2. `docker compose --profile models up` adds the model server.
3. `api` reads `TIRVI_MODELS_URL`; with profile off, points at fixture-backed mock.

#### Edge Cases
- Backend dev forgets profile; pipeline returns "model service unreachable" with fix-it pointer.

#### Acceptance Criteria
```gherkin
Given the default profile is selected
When `docker compose up` is run
Then `models` service is NOT started
And `api` health check passes against fixture fallback
```

#### Dependencies
- DEP-INT to E00-F03 (fakes for fixture fallback)

#### Non-Functional Considerations
- Resource: peak resident memory ≤ 4 GB on default profile.
- DX: profile choice surfaced in `make doctor` output.

#### Open Questions
- Does the lite profile mock cover all NLP endpoints or only the most-used?
