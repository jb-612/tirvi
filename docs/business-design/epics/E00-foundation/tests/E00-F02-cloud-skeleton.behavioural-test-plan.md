# E00-F02 — Cloud Skeleton: Behavioural Test Plan

## Behavioural Scope
Covers SRE behaviour during apply, recovery from failed apply, and human
escalation when terraform state is locked or drifted.

## Human Behaviour Patterns Covered
| Behaviour | Persona | Risk | Test Method |
|-----------|---------|------|------------|
| First-time apply, missing API enable | P04 SRE | gives up after 2 failures | actionable error → enable API hint |
| Mid-apply Ctrl-C | P04 SRE | TF state lock left over | unlock instructions surfaced |
| Drift after manual gcloud edit | P04 SRE | apply overwrites manual fix | drift detection runs nightly |

---

## Behavioural Scenarios

### BT-005: SRE applies before enabling APIs
**Persona:** P04 SRE
**Intent:** stand up dev env in 10 min before standup
**Human behaviour:** runs apply; provider returns API not enabled; SRE follows hint
**System expectation:** error names the API and links to enablement command
**Acceptance criteria:** SRE recovers within one command

### BT-006: Apply interrupted; lock left behind
**Persona:** P04 SRE
**Intent:** rerun apply after laptop crash
**Human behaviour:** runs apply; sees "state locked"
**System expectation:** lock file owned by previous run; clear unlock instruction; lock TTL
**Escalation path:** docs link to `terraform force-unlock` with safety checklist

### BT-007: Pair-review apply on prod
**Persona:** two SREs
**Intent:** prod change
**Human behaviour:** one runs plan; other reads plan; second SRE approves
**System expectation:** plan stored as artifact; apply consumes the same plan file
**Collaboration expectation:** approval recorded in PR comment

### BT-008: Manual gcloud change leads to drift
**Persona:** P04 SRE under incident pressure
**Intent:** patch IAM during outage
**Human behaviour:** runs gcloud manually; forgets to backport to TF
**System expectation:** nightly drift detection PR opens with diff
**Acceptance criteria:** SRE merges drift fix within next sprint

## Edge Behaviour
- TF rejects unknown variable → SRE reads doc, finds it removed in this version.
- Region change is detected as destroy/create; behavioural test confirms a
  pre-apply warning surfaces this.

## Misuse Behaviour
- SRE applies prod plan in dev workspace; pre-apply guard rejects with
  workspace check.
- SRE attempts to disable lifecycle rule on `audio/`; plan refuses unless
  ADR justification cited.

## Recovery Behaviour
- Failed apply mid-IAM grant: TF re-apply continues from last known good.
- Terraform state corruption: backup restore process documented and rehearsed
  quarterly.

## Collaboration Breakdown Tests
- SRE on call cannot reach pair: emergency apply allowed only with team-lead
  approval comment in incident channel.
- Slack down: incident bridge phone fallback documented.

## Open Questions
- How long should the apply lock TTL be — 15 min or 60 min?
