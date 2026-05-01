# ADR-036 — exam-review-portal — Auth Deferred as NFR

**Status:** Accepted
**Feature refs:** N04/F33
**Bounded context:** exam_review / platform
**Date:** 2026-05-01

---

## Context

The Exam Review Portal (N04/F33) is used by university accommodation
coordinators, QA reviewers, and pipeline developers to inspect pipeline
voiceover artifacts and annotate per-word quality issues before an exam is
distributed to students. The portal serves intermediate pipeline output from
a local `output/<N>/` directory via a small HTTP server (`scripts/run_demo.py`).

Access control to the portal is desirable. However, implementing an
authentication or authorization layer requires infrastructure that does not
yet exist in this project:

- No identity service or user model
- No session management layer
- No role schema (admin / reviewer / developer)
- No OAuth2 provider integration
- No HTTPS configuration beyond localhost

Coupling the F33 functional build to a security ceremony that has no
infrastructure foundation would delay the admin feedback loop unnecessarily
and create a false sense of security (a half-implemented auth layer is
worse than an explicitly acknowledged open-by-default posture).

HLD §3.2 acknowledges auth is a future concern (`POST /documents/{id}/feedback`
carries an auth stub); ADR-008 records auth as a Proposed decision scoped to
"anonymous session vs. accounts" for MVP — not yet resolved.

BT-218 (QA scenario) explicitly validates the "no-login required" posture for
staging review and documents it as an intentional risk-acknowledged decision.

---

## Decision

The Exam Review Portal (N04/F33) ships with **no authentication or
authorization layer**. Specifically:

1. The `/review` endpoint and the `do_POST /feedback` handler in
   `scripts/run_demo.py` require no credentials.
2. The portal is **localhost-only** during the POC phase. It MUST NOT be
   exposed on a public network or a shared staging environment until the auth
   NFR feature is implemented.
3. The `scripts/run_demo.py` entry point carries an explicit
   `# AUTH_GATE TODO: add auth before exposing over network` comment as a
   mandatory reminder for any future deployment change.
4. A separate auth NFR feature must be designed and implemented before any
   multi-user or network-accessible deployment of the portal.

---

## Consequences

**Positive:**
- The functional admin review loop (artifact inspection + word annotation +
  feedback export) can be built and validated without blocking on security
  infrastructure.
- Avoids false security — the open-by-default posture is explicit and
  documented, not silently absent.
- Aligns with the POC scope: single-user, localhost, developer-controlled
  environment.

**Negative:**
- The portal MUST NOT be deployed to any shared or network-accessible
  environment without first shipping the auth NFR.
- Any accidental `--host 0.0.0.0` or port-forwarding would expose pipeline
  artifacts without access control.

**Mitigation:**
- `AUTH_GATE TODO` comment in `run_demo.py` is a mandatory code artifact.
- This ADR is referenced in `design.md D-03` and in `traceability.yaml
  adr_refs` so it appears in every traceability query for F33.
- The auth NFR is a blocking gate for any network deployment, not a
  nice-to-have.

---

## Alternatives Considered

**1. Basic HTTP auth (username/password in run_demo.py)**
Rejected. Basic auth adds friction (password management, sharing credentials)
without providing meaningful security. It is not transportable to a real auth
system and gives a false sense of protection.

**2. OAuth2 / OIDC from day one**
Rejected. No OAuth2 provider, no user model, no redirect URI infrastructure
exists. Implementing this before the functional portal is working would take
longer than building the portal itself, and the result would be untestable
without the full cloud stack.

**3. IP allowlist on the demo server**
Rejected. A hardcoded IP allowlist in a localhost demo server is fragile,
not maintainable, and not a real access control mechanism.

---

## References

- ADR-023: POC player ships as vanilla HTML; Next.js deferred to MVP
- ADR-008: Auth in MVP (anonymous session vs. accounts) — Proposed
- PRD §10: Admin feedback loop and success metrics
- BT-218: QA reviewer validates run before production promotion (no-login scenario)
- HLD §3.2: Backend API — `POST /documents/{id}/feedback` (auth stub)
