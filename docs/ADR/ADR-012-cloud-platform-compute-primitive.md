---
adr_id: ADR-012
title: Cloud compute primitive — Cloud Run vs. App Engine vs. Functions
status: Accepted
date: 2026-04-29
deciders: [tirvi research, F02-cloud-skeleton]
bounded_context: cloud-platform
hld_refs: ["HLD-§7/DeploymentTopology", "HLD-§3.2/BackendAPI", "HLD-§3.3/Worker"]
related_features: [F02-cloud-skeleton]
related_adrs: [ADR-010]
---

# ADR-012 — Cloud compute primitive

## Status

**Accepted** (2026-04-29). Resolves the user-facing ask "GCP App Service"
flagged in HLD §7 footnote.

## Context

PRD §9 calls for "GCP managed services; no self-managed VMs." The user
phrased this as "GCP App Service" — a product GCP doesn't ship under that
name. HLD §7 lists the closest managed equivalents: **Cloud Run**,
**App Engine Standard/Flex**, **Cloud Functions**, **GKE Autopilot**.
The choice anchors every other infra decision (autoscale model, packaging,
cold-start budget, Cloud Tasks integration, observability).

The tirvi pipeline is *request-driven*: each pipeline stage is a discrete
short HTTP-triggered task pushed by Cloud Tasks. Same image, different
entrypoints. Targets: scale-to-zero, sub-second autoscale, ≤ 30 s p50
time-to-first-audio for a 5-page exam.

## Decision

Use **Cloud Run services** for both `tirvi-api` and `tirvi-worker`. Same
container image; entrypoints differ. Scale-to-zero by default; per-service
`min-instances=1` opt-in for latency-sensitive paths (the OCR/NLP worker
during business hours, per research §3.8 NFR analysis). Cloud Tasks pushes
HTTP to the worker service.

## Consequences

**Positive**

- Scale-to-zero matches the cost posture in HLD §7.5 and PRD §7.4.
- Cloud Tasks → Cloud Run HTTP push is the documented pattern (per
  Google's own "Choose Cloud Tasks or Pub/Sub" matrix).
- Per-process container model matches the Compose dev shape from F01 —
  one process per container, clean log separation, per-service crash
  boundary.
- `--cpu-boost` + `min-instances=1` mitigate the cold-start contribution
  to the 30 s p50 first-audio target.

**Negative**

- 60-minute request-timeout ceiling on Cloud Run services — not relevant
  for tirvi's per-block work but worth knowing.
- Cloud Run pricing is per-vCPU-second; aggressive caching (F32) is
  mandatory to keep $0.02/page amortized.

## Alternatives

**A1: App Engine Standard/Flex** (rejected)

- More opinionated runtime, older container story, weaker
  Cloud-Tasks-push integration. No material upside for tirvi's shape.

**A2: Cloud Functions / Cloud Run Functions** (rejected)

- Per-function packaging; cold-start budget tighter; package-size
  limits. The worker pipeline carries Hebrew NLP weights — too big.

**A3: Cloud Run Jobs** (rejected for the worker; not applicable to api)

- Run-to-completion semantics fit batch ETL, not request-driven
  per-page work. Re-evaluate post-MVP if a nightly bench job emerges.

**A4: GKE Autopilot** (rejected)

- Overkill for 10–100 jobs/day MVP scale. Re-evaluate when GPU-accelerated
  TTS or persistent model-server traffic dominates (post-MVP, see ADR-010).

## References

- HLD §7 (Deployment topology — GCP)
- HLD §3.2 / §3.3 (Backend API + Worker on Cloud Run)
- Research §3.1 (Compute platform — Cloud Run for API and worker)
- Google Cloud — "Executing asynchronous tasks" (Cloud Run + Cloud Tasks)
- Google Cloud — "Choose Cloud Tasks or Pub/Sub"
- ADR-010 (NLP compute primitive — informs `min-instances` and CPU/GPU)
