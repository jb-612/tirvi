# E00-F02 — Cloud Run + Cloud Tasks + GCS Skeleton (Terraform)

## Source Basis
- PRD: §9 Constraints (Cloud Run, Cloud Tasks, Cloud Storage)
- HLD: §7 Deployment topology, §12 OQ#1 (GCP App Service → Cloud Run)
- Research: src-003 §3 architecture changes #2 + #3, §10 Phase 0 F0.2
- Assumptions: ASM05 (practice-mode framing fits scale-to-zero)

## Personas
| Persona | Role | Goal | Pain Point | Success Criterion |
|---------|------|------|-----------|------------------|
| P04 Operator/SRE | runs prod | provision `tirvi-{env}` reproducibly | drift between dev and prod | `terraform apply` from clean state ≤ 15 min |
| P08 Backend Dev | deploys CI artifacts | push image and trigger Cloud Tasks | env config skew | per-env Terraform workspace isolates state |

## Collaboration Model
1. Primary: SRE.
2. Supporting: backend dev (consumes outputs); finance owner (sees billing labels).
3. System actors: Terraform provider, GCP IAM, Cloud Run service, Cloud Tasks queues, GCS bucket, Secret Manager.
4. Approvals: prod apply requires SRE pair-review.
5. Handoff: outputs → CI pipeline (E00-F04) for image deploy.
6. Failure recovery: `terraform plan` flags diffs; tainted resources re-applied.

## Behavioural Model
- Hesitation: SRE unsure whether to merge dev/staging/prod into one workspace.
- Rework: missed IAM binding, deploy fails, IAM patched.
- Partial info: secrets not yet stored; Terraform allows null with explicit flag.
- Abandoned flow: apply interrupted; lock file recovery documented.

---

## User Stories

### Story 1: Apply infrastructure for a new environment

**As an** SRE
**I want** Terraform to provision `tirvi-api`, `tirvi-worker`, `tirvi-jobs` queues, `tirvi-{env}` bucket, secrets, and IAM in one workspace
**So that** I can stand up a new environment reproducibly.

#### Preconditions
- GCP project exists; Terraform service account has Owner on project.
- Workspace `dev|staging|prod` selected.

#### Main Flow
1. `terraform workspace select dev && terraform apply`
2. Provider creates Cloud Run services with `min-instances=0` (dev) / `1` (prod).
3. Five Cloud Tasks queues created (`ocr`, `normalize`, `nlp`, `plan`, `synthesize`).
4. Bucket `tirvi-dev` created with lifecycle rule (24h on `pdfs/pages/plans/manifests/`).
5. Outputs printed: API URL, worker URL, bucket name, queue names.

#### Alternative Flows
- Re-run after image bump: only Cloud Run revision changes.
- Destroy: `terraform destroy` keeps `audio/` bucket if shareable cache flag set.

#### Edge Cases
- Project lacks Cloud Run API enabled; provider fails with actionable error.
- Lifecycle rule on `audio/` accidentally configured; plan diff catches it.

#### Acceptance Criteria
```gherkin
Given a fresh GCP project with billing enabled
When SRE runs `terraform apply` for dev workspace
Then within 15 minutes all five queues, both services, bucket, and IAM exist
And the bucket lifecycle is 24h on `pdfs/`, `pages/`, `plans/`, `manifests/`
And `audio/` has no auto-delete rule
```

#### Data and Business Objects
- `Environment` (dev|staging|prod), `RetentionPolicy`, `QueueDefinition`.

#### Dependencies
- DEP-EXT-GCP project + billing
- DEP-INT to E11-F01 (TTL automation) and E08-F03 (audio cache lifetime)

#### Non-Functional Considerations
- Reliability: idempotent apply.
- Cost: scale-to-zero default in dev / staging.
- Security: secrets in Secret Manager, never in TF state plain text.
- Auditability: TF state remote-locked with versioning.

#### Open Questions
- Use Workload Identity Federation for CI deploy or GCP-managed key?

---

### Story 2: Cloud Tasks per-stage queue isolates retries

**As an** SRE
**I want** one Cloud Tasks queue per pipeline stage with independent retry budgets
**So that** an OCR storm doesn't starve TTS retries.

#### Preconditions
- Workspace already applied.
- HLD §3.3 stage list (ocr / normalize / nlp / plan / synthesize) is canonical.

#### Main Flow
1. Each queue has its own `maxAttempts`, `minBackoff`, `maxBackoff`, `maxConcurrent`.
2. Worker entrypoint dispatches by URL path matching queue name.
3. Per-queue dashboards show backlog and oldest message age.

#### Edge Cases
- TTS provider rate-limit storm fills `synthesize` queue; OCR processing unaffected.
- Stage rename rolls forward but old queue retains in-flight tasks; rename plan documented.

#### Acceptance Criteria
```gherkin
Given five queues are configured
When the synthesize queue is throttled at maxConcurrent=2
Then the ocr/normalize/nlp/plan queues continue at their own concurrency
And per-queue oldest-age metrics are emitted to Cloud Monitoring
```

#### Dependencies
- DEP-INT to E08-F03 (cache reduces synthesize traffic)
- DEP-INT to E10-F05 (cost telemetry reads queue metrics)

#### Non-Functional Considerations
- Reliability: dead-letter destination for permanent failures.
- Observability: queue metrics consumed by Stage E10.

#### Open Questions
- Single dead-letter queue for all stages or per-stage DLQs?
